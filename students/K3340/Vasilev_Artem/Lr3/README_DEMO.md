# README_DEMO: демонстрация ЛР3

Файл описывает, как протестировать и показать ЛР3 преподавателю на Windows через PowerShell.

Рабочая папка:

```powershell
cd D:\new\my_files\study\WebDev\ITMO_ICT_WebDevelopment_tools_2025-2026\students\K3340\Vasilev_Artem\Lr3
```

## 1. Что реализовано

В ЛР3 реализовано:

- `Dockerfile` для основного FastAPI API.
- `parser_service/Dockerfile` для отдельного parser-service.
- `docker-compose.yml` для запуска всех сервисов.
- PostgreSQL как основная база данных.
- Redis как broker и result backend для Celery.
- Celery worker для фонового выполнения задач.
- Celery Beat для периодического запуска задачи парсинга.
- HTTP-вызов parser-service из основного API.
- Синхронный endpoint основного API: `POST /api/v1/parser/parse-sync`.
- Асинхронный endpoint через очередь: `POST /api/v1/parser/parse-async`.
- Endpoint проверки статуса Celery-задачи: `GET /api/v1/parser/tasks/{task_id}`.
- Periodic task: `worker.tasks.parse_default_urls_task`, запускается каждые 30 минут, timezone `UTC`.

Важное поведение: parser-service использует перенесенную из ЛР2 функцию `parse_and_save`, поэтому парсер не только возвращает JSON, но и сохраняет найденные данные в PostgreSQL в таблицы `users`, `categories`, `tasks`, `task_categories`.

## 2. Подготовка к запуску

Проверить, что Docker Desktop запущен:

```powershell
docker version
docker compose version
```

Перейти в папку ЛР3:

```powershell
cd D:\new\my_files\study\WebDev\ITMO_ICT_WebDevelopment_tools_2025-2026\students\K3340\Vasilev_Artem\Lr3
```

Создать `.env` из `.env.example`:

```powershell
Copy-Item .env.example .env
```

Собрать контейнеры:

```powershell
docker compose build
```

Запустить проект:

```powershell
docker compose up
```

Если нужно запустить в фоне:

```powershell
docker compose up -d
```

## 3. Миграции Alembic

После запуска контейнеров применить миграции внутри `api`-контейнера:

```powershell
docker compose exec api alembic upgrade head
```

Проверить, что таблицы появились:

```powershell
docker compose exec postgres psql -U postgres -d time_manager -c "\dt"
```

Ожидаемый результат: в списке таблиц есть `users`, `tasks`, `categories`, `task_categories`, `time_logs`, `daily_plans`, `daily_plan_tasks`, `notifications`, `alembic_version`.

Проверить текущую версию миграции:

```powershell
docker compose exec postgres psql -U postgres -d time_manager -c "select * from alembic_version;"
```

## 4. Проверка контейнеров и логов

Посмотреть статус контейнеров:

```powershell
docker compose ps
```

Ожидаемо должны быть запущены сервисы:

- `postgres`
- `redis`
- `api`
- `parser-service`
- `celery-worker`
- `celery-beat`

Посмотреть логи:

```powershell
docker compose logs api
docker compose logs parser-service
docker compose logs celery-worker
docker compose logs celery-beat
docker compose logs redis
docker compose logs postgres
```

Следить за логами в реальном времени:

```powershell
docker compose logs -f api
docker compose logs -f parser-service
docker compose logs -f celery-worker
docker compose logs -f celery-beat
```

## 5. Endpoint-ы для тестирования

Реальные endpoint-ы проекта:

- Main API: `GET http://localhost:8000/health`
- Main API v1: `GET http://localhost:8000/api/v1/health`
- Parser-service: `GET http://localhost:8001/health`
- Parser-service: `POST http://localhost:8001/parse`
- Main API sync: `POST http://localhost:8000/api/v1/parser/parse-sync`
- Main API async: `POST http://localhost:8000/api/v1/parser/parse-async`
- Main API task status: `GET http://localhost:8000/api/v1/parser/tasks/{task_id}`

В PowerShell лучше использовать `curl.exe`, чтобы не попасть в alias `curl` для `Invoke-WebRequest`. JSON в примерах экранирован в формате, который был проверен на Windows PowerShell: `'{\\\"key\\\":\\\"value\\\"}'`.

### 5.1 Main API health

Команда:

```powershell
curl.exe http://localhost:8000/health
```

Ожидаемый успешный ответ:

```json
{"status":"ok","service":"Time Manager API","version":"0.1.0"}
```

Что доказывает тест: основной API-контейнер запущен, FastAPI-приложение отвечает.

### 5.2 Main API v1 health

Команда:

```powershell
curl.exe http://localhost:8000/api/v1/health
```

Ожидаемый успешный ответ:

```json
{"status":"ok","service":"Time Manager API","version":"0.1.0"}
```

Что доказывает тест: v1 router подключен через `API_V1_PREFIX=/api/v1`.

### 5.3 Parser-service health

Команда:

```powershell
curl.exe http://localhost:8001/health
```

Ожидаемый успешный ответ:

```json
{"status":"ok","service":"parser-service"}
```

Что доказывает тест: отдельный parser-service запущен и доступен на порту `8001`.

### 5.4 Parser-service POST /parse

Команда:

```powershell
curl.exe -X POST http://localhost:8001/parse `
  -H "Content-Type: application/json" `
  -d '{\\\"urls\\\":[\\\"https://www.peopleperhour.com/freelance-jobs/technology-programming\\\"],\\\"workers\\\":4}'
```

Ожидаемый успешный ответ имеет вид:

```json
{
  "method": "asyncio",
  "started_at": 123456.0,
  "urls": 1,
  "saved": 0,
  "extracted": 0,
  "ok": 1,
  "errors": 0,
  "elapsed_seconds": 1.23,
  "items": []
}
```

Числа могут отличаться. `saved` и `extracted` зависят от доступности сайта и HTML-структуры страницы.

Что доказывает тест: parser-service принимает JSON, запускает перенесенную parser-логику из ЛР2 и пытается сохранить результат в PostgreSQL.

### 5.5 Sync-вызов parser-service из Main API

Команда:

```powershell
curl.exe -X POST http://localhost:8000/api/v1/parser/parse-sync `
  -H "Content-Type: application/json" `
  -d '{\\\"urls\\\":[\\\"https://www.peopleperhour.com/freelance-jobs/technology-programming\\\"],\\\"workers\\\":4}'
```

Ожидаемый успешный ответ совпадает по структуре с ответом parser-service:

```json
{
  "method": "asyncio",
  "started_at": 123456.0,
  "urls": 1,
  "saved": 0,
  "extracted": 0,
  "ok": 1,
  "errors": 0,
  "elapsed_seconds": 1.23,
  "items": []
}
```

Что доказывает тест: клиент обращается к основному API, а основной API делает HTTP POST в parser-service по `PARSER_SERVICE_URL=http://parser-service:8001`.

### 5.6 Async-вызов через Celery

Команда:

```powershell
curl.exe -X POST http://localhost:8000/api/v1/parser/parse-async `
  -H "Content-Type: application/json" `
  -d '{\\\"urls\\\":[\\\"https://www.peopleperhour.com/freelance-jobs/technology-programming\\\"],\\\"workers\\\":4}'
```

Ожидаемый успешный ответ:

```json
{"task_id":"<celery-task-id>","status":"queued"}
```

Что доказывает тест: основной API не запускает парсер сразу, а ставит задачу в Celery через Redis.

Сохранить `task_id` в переменную PowerShell:

```powershell
$response = curl.exe -s -X POST http://localhost:8000/api/v1/parser/parse-async `
  -H "Content-Type: application/json" `
  -d '{\\\"urls\\\":[\\\"https://www.peopleperhour.com/freelance-jobs/technology-programming\\\"],\\\"workers\\\":4}' | ConvertFrom-Json

$taskId = $response.task_id
$taskId
```

### 5.7 Проверка статуса Celery task

Команда:

```powershell
curl.exe http://localhost:8000/api/v1/parser/tasks/$taskId
```

Или вручную:

```powershell
curl.exe http://localhost:8000/api/v1/parser/tasks/<celery-task-id>
```

Ожидаемый ответ во время выполнения:

```json
{
  "task_id": "<celery-task-id>",
  "status": "PENDING",
  "result": null,
  "error": null
}
```

Ожидаемый ответ после успешного выполнения:

```json
{
  "task_id": "<celery-task-id>",
  "status": "SUCCESS",
  "result": {
    "method": "asyncio",
    "urls": 1,
    "saved": 0,
    "extracted": 0,
    "ok": 1,
    "errors": 0
  },
  "error": null
}
```

Что доказывает тест: Redis result backend хранит состояние задачи, а основной API умеет получить статус и результат.

## 6. Сценарий демонстрации преподавателю

1. Показать структуру проекта:

```powershell
Get-ChildItem
```

Обратить внимание на папки `app`, `parser`, `parser_service`, `worker`, `alembic`.

2. Показать `docker-compose.yml`:

```powershell
Get-Content .\docker-compose.yml
```

Объяснить, что compose запускает `postgres`, `redis`, `api`, `parser-service`, `celery-worker`, `celery-beat`.

3. Показать Dockerfile API:

```powershell
Get-Content .\Dockerfile
```

Объяснить, что он ставит зависимости и запускает `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

4. Показать Dockerfile parser-service:

```powershell
Get-Content .\parser_service\Dockerfile
```

Объяснить, что это отдельный FastAPI-сервис на порту `8001`.

5. Запустить проект:

```powershell
docker compose up --build
```

6. Применить миграции:

```powershell
docker compose exec api alembic upgrade head
```

7. Проверить health:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8001/health
```

8. Показать прямой parser-service `/parse`:

```powershell
curl.exe -X POST http://localhost:8001/parse `
  -H "Content-Type: application/json" `
  -d '{\\\"urls\\\":[\\\"https://www.peopleperhour.com/freelance-jobs/technology-programming\\\"],\\\"workers\\\":4}'
```

9. Показать sync-вызов из API:

```powershell
curl.exe -X POST http://localhost:8000/api/v1/parser/parse-sync `
  -H "Content-Type: application/json" `
  -d '{\\\"urls\\\":[\\\"https://www.peopleperhour.com/freelance-jobs/technology-programming\\\"],\\\"workers\\\":4}'
```

10. Показать Redis и Celery worker:

```powershell
docker compose ps
docker compose logs celery-worker
docker compose logs redis
```

11. Показать async-вызов:

```powershell
$response = curl.exe -s -X POST http://localhost:8000/api/v1/parser/parse-async `
  -H "Content-Type: application/json" `
  -d '{\\\"urls\\\":[\\\"https://www.peopleperhour.com/freelance-jobs/technology-programming\\\"],\\\"workers\\\":4}' | ConvertFrom-Json

$taskId = $response.task_id
$response
```

12. Показать проверку `task_id`:

```powershell
curl.exe http://localhost:8000/api/v1/parser/tasks/$taskId
```

13. Показать Celery Beat и periodic task:

```powershell
Get-Content .\worker\celery_app.py
docker compose logs celery-beat
```

Объяснить, что `worker.tasks.parse_default_urls_task` запускается каждые 30 минут. Если не ждать 30 минут на защите, достаточно показать `beat_schedule` и запущенный контейнер `celery-beat`.

14. Показать сохранение данных в PostgreSQL:

```powershell
docker compose exec postgres psql -U postgres -d time_manager -c "select id, username, email from users order by id desc limit 10;"
docker compose exec postgres psql -U postgres -d time_manager -c "select id, name, owner_id from categories order by id desc limit 10;"
docker compose exec postgres psql -U postgres -d time_manager -c "select id, title, owner_id from tasks order by id desc limit 10;"
docker compose exec postgres psql -U postgres -d time_manager -c "select id, task_id, category_id, label from task_categories order by id desc limit 10;"
```

## 7. Команды проверки БД

Зайти в postgres-контейнер:

```powershell
docker compose exec postgres sh
```

Открыть `psql` из контейнера:

```powershell
psql -U postgres -d time_manager
```

Внутри `psql` посмотреть таблицы:

```sql
\dt
```

Выйти из `psql`:

```sql
\q
```

Выйти из контейнера:

```powershell
exit
```

Одноразовые команды без входа в shell:

```powershell
docker compose exec postgres psql -U postgres -d time_manager -c "\dt"
docker compose exec postgres psql -U postgres -d time_manager -c "select id, username, email, is_active from users order by id desc limit 10;"
docker compose exec postgres psql -U postgres -d time_manager -c "select id, name, owner_id from categories order by id desc limit 10;"
docker compose exec postgres psql -U postgres -d time_manager -c "select id, title, priority, status, owner_id from tasks order by id desc limit 10;"
docker compose exec postgres psql -U postgres -d time_manager -c "select id, task_id, category_id, label from task_categories order by id desc limit 10;"
```

Если парсер ничего не сохранил, но запросы к таблицам работают, значит БД и миграции в порядке, а проблема может быть во внешнем сайте или HTML-селекторах.

## 8. Что говорить преподавателю

Короткий текст:

> В ЛР3 я упаковал приложение из ЛР1 и парсер из ЛР2 в Docker Compose. Основной сервис `api` отвечает за публичный REST API. Парсер вынесен в отдельный `parser-service`, чтобы отделить логику получения данных с внешних сайтов от основного приложения. PostgreSQL используется как основная база данных, потому что модели и миграции из ЛР1 уже рассчитаны на PostgreSQL.

Про Docker:

> Docker нужен, чтобы все зависимости запускались одинаково: API, parser-service, PostgreSQL, Redis, Celery worker и Celery Beat поднимаются одной командой `docker compose up --build`.

Про parser-service:

> Parser-service вынесен отдельно, потому что парсинг может быть долгой или нестабильной операцией. Так основной API не смешивает бизнес-API и работу с внешними сайтами.

Про Redis:

> Redis используется как брокер сообщений Celery и как backend для хранения результата задачи. Через него API передает задачу worker-у и потом получает статус.

Про Celery:

> Celery нужен для фонового выполнения парсинга. Клиент получает `task_id` сразу, а сам парсинг выполняется в `celery-worker`.

Про sync и async:

> Sync endpoint `/parse-sync` ждет ответа parser-service и возвращает результат сразу. Async endpoint `/parse-async` только ставит задачу в очередь и возвращает `task_id`; статус и результат проверяются отдельным endpoint-ом.

Про Celery Beat:

> Celery Beat нужен для периодических задач. В проекте он каждые 30 минут ставит в очередь задачу `parse_default_urls_task`, которая парсит список `DEFAULT_URLS`.

## 9. Troubleshooting

### Порт занят

Симптом: Docker пишет, что порт `8000`, `8001`, `5432` или `6379` уже используется.

Проверить процессы:

```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :8001
netstat -ano | findstr :5432
netstat -ano | findstr :6379
```

Решение: остановить конфликтующий процесс или поменять host-port в `docker-compose.yml`. По заданию текущие порты: `8000`, `8001`, `5432`, `6379`.

### БД не готова

Симптом: API или parser-service пишет ошибку подключения к PostgreSQL.

Проверить статус:

```powershell
docker compose ps
docker compose logs postgres
```

В compose есть healthcheck `pg_isready`, поэтому `api` ждет healthy-состояние `postgres`.

### Миграции не применены

Симптом: ошибки вида `relation "users" does not exist` или `relation "tasks" does not exist`.

Решение:

```powershell
docker compose exec api alembic upgrade head
docker compose exec postgres psql -U postgres -d time_manager -c "\dt"
```

### Parser-service недоступен

Симптом: `/api/v1/parser/parse-sync` возвращает `502 Bad Gateway`.

Проверить:

```powershell
docker compose ps
docker compose logs parser-service
curl.exe http://localhost:8001/health
```

Проверить переменную:

```powershell
docker compose exec api env | findstr PARSER_SERVICE_URL
```

Ожидаемо: `PARSER_SERVICE_URL=http://parser-service:8001`.

### Celery task остается PENDING

Симптом: `GET /api/v1/parser/tasks/{task_id}` долго возвращает `PENDING`.

Проверить Redis и worker:

```powershell
docker compose ps
docker compose logs redis
docker compose logs celery-worker
```

Проверить переменные:

```powershell
docker compose exec api env | findstr CELERY
docker compose exec celery-worker env | findstr CELERY
```

### Сайты парсинга недоступны или изменили HTML

Симптом: `errors > 0`, `extracted = 0` или `saved = 0`.

Причины:

- внешний сайт недоступен;
- сайт заблокировал запрос;
- изменилась HTML-структура;
- селекторы из ЛР2 больше не находят карточки.

Проверить логи:

```powershell
docker compose logs parser-service
docker compose logs celery-worker
```

### Ошибка подключения к Redis

Симптом: API не может поставить задачу в очередь или Celery worker не стартует.

Проверить:

```powershell
docker compose ps
docker compose logs redis
docker compose exec redis redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

### Ошибка подключения к PostgreSQL

Симптом: parser-service или API не могут сохранить данные.

Проверить:

```powershell
docker compose logs postgres
docker compose exec postgres pg_isready -U postgres -d time_manager
docker compose exec api env | findstr DATABASE_URL
docker compose exec parser-service env | findstr DATABASE_URL
```

Ожидаемо `DATABASE_URL` должен содержать `postgres:5432`, а не `localhost:5432`.

## 10. Чеклист сдачи

Перед демонстрацией проверить:

- [ ] Docker Desktop запущен.
- [ ] `.env` создан из `.env.example`.
- [ ] `docker compose build` выполнен без ошибок.
- [ ] `docker compose up` запустил все сервисы.
- [ ] `docker compose ps` показывает `postgres`, `redis`, `api`, `parser-service`, `celery-worker`, `celery-beat`.
- [ ] Alembic-миграции применены через `docker compose exec api alembic upgrade head`.
- [ ] `GET /health` работает.
- [ ] `GET /api/v1/health` работает.
- [ ] `GET parser-service /health` работает.
- [ ] `POST parser-service /parse` работает.
- [ ] `POST /api/v1/parser/parse-sync` работает.
- [ ] `POST /api/v1/parser/parse-async` возвращает `task_id`.
- [ ] `GET /api/v1/parser/tasks/{task_id}` возвращает статус задачи.
- [ ] `celery-worker` обрабатывает задачу, это видно в логах.
- [ ] `celery-beat` запущен, это видно в `docker compose ps` и логах.
- [ ] После парсинга данные появились в `users`, `categories`, `tasks`, `task_categories` или есть понятная причина, почему внешний сайт не отдал данные.

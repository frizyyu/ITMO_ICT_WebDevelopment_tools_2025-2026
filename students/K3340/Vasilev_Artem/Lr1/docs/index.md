# Лабораторная работа 1

## Тема

Разработка веб-приложения для управления задачами и контроля сроков выполнения.

---

## Описание приложения

Разработанное приложение представляет собой серверный API для управления задачами.

Приложение позволяет:

* создавать задачи и управлять ими
* задавать приоритет и статус задач
* назначать категории задач
* добавлять теги к задачам
* связывать задачи и теги (many-to-many)
* хранить дополнительные данные о связи (заметка и уровень важности)
* получать задачи с вложенными связанными объектами

---

## Ссылки на GitHub

Репозиторий:
[https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026](https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026)

Практика 1.1:
[https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/task1](https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/task1)

Практика 1.2:
[https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/task2](https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/task2)

Практика 1.3:
[https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/task3](https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/task3)

Лабораторная работа:
[https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/lab](https://github.com/frizyyu/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3340/Vasilev_Artem/Lr1/lab)

---

## Используемые технологии

* FastAPI
* SQLModel
* PostgreSQL
* Alembic
* python-dotenv

---

## Подключение к БД

Файл: `connection.py`

```python
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
```

---

## Модели данных

Всего используется 4 таблицы.

---

### 1. Category

Поля:

* id
* name
* color

Связи:

* one-to-many с Task

---

### 2. Task

Поля:

* id
* title
* description
* priority
* status
* due_at
* category_id

Связи:

* many-to-one с Category
* many-to-many с Tag

---

### 3. Tag

Поля:

* id
* name

Связи:

* many-to-many с Task

---

### 4. TaskTagLink

Ассоциативная таблица many-to-many между Task и Tag.

Поля:

* task_id
* tag_id
* note
* importance_level

---

## Связи между таблицами

* Category → Task : one-to-many
* Task ↔ Tag : many-to-many через TaskTagLink

Ассоциативная сущность содержит дополнительные поля:

* note
* importance_level

---

## Миграции Alembic

Файлы:

* `alembic.ini`
* `migrations/env.py`
* `migrations/versions/*.py`

Используемые команды:

```bash
alembic init migrations
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

После применения миграций создаётся таблица:

```sql
SELECT * FROM alembic_version;
```

---

## Все реализованные эндпоинты

### Сервисные

* GET / — проверка доступности API

---

### Category

* POST /categories — создание категории
* GET /categories — список категорий

---

### Tag

* POST /tags — создание тега
* GET /tags — список тегов

---

### Task

* POST /tasks — создание задачи
* GET /tasks — список задач
* GET /tasks/{id} — получение задачи
* PATCH /tasks/{id} — обновление задачи
* DELETE /tasks/{id} — удаление задачи

---

### Связи

* POST /tasks/{task_id}/tags/{tag_id} — привязка тега к задаче

---

### Детализация

* GET /tasks/{id}/details

Возвращает:

* данные задачи
* категорию
* список тегов с дополнительными полями

---

## Вложенные модели в GET-запросах

### GET /tasks/{id}/details

Возвращает:

* задачу
* объект категории
* список тегов

Пример:

```json
{
  "id": 1,
  "title": "Finish lab",
  "category": {
    "id": 1,
    "name": "Work"
  },
  "tags": [
    {
      "id": 1,
      "name": "urgent",
      "note": "main migration topic",
      "importance_level": 5
    }
  ]
}
```

---

## Примеры ключевых файлов

### Главный файл приложения

```python
from fastapi import FastAPI

app = FastAPI(title="Task Manager API")


@app.get("/")
def root():
    return {"message": "Task Manager API"}
```

---

## Запуск проекта

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

---

## Swagger UI

Документация доступна по адресу:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Вывод

В рамках лабораторной работы было разработано серверное приложение на FastAPI для управления задачами. В проекте реализованы:

* структура FastAPI-приложения
* PostgreSQL и ORM SQLModel
* миграции Alembic
* CRUD API
* связи one-to-many и many-to-many
* ассоциативная таблица с дополнительными полями
* вложенные ответы для связанных моделей

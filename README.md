![workflow](https://github.com/sakovdmitry/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
адрес для доступа:
http://51.250.16.72/api/v1/

# Описание проекта
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором.

# Шаблон наполнения .env файла

	DB_ENGINE=django.db.backends.postgresql
	DB_NAME=postgres
	POSTGRES_USER=postgres
	POSTGRES_PASSWORD=postgres
	DB_HOST=db
	DB_PORT=5432
	SECRET_KEY = 'your secret key'

## Запуск проекта
Для начала склонируйте репозиторий с github
```
git clone git@github.com:sakovdmitry/yamdb_final.git
```
Комманда git push является триггером workflow (yamdb_workflow.yaml).
При выполнении команды git push запускается набор блоков следующих команд:
1. Тестирование проекта.
2. Сборка и публикация образа.
3. Автоматический деплой.
4. Отправка уведомления в персональный чат.

В дальнейшем необходимо установить соединение с сервером и выполнить следующие команды:

- Выполнить миграции
```
sudo docker-compose exec web python manage.py migrate
```
- Создать суперпользователя
```
sudo docker-compose exec web python manage.py createsuperuser
```
- Сформируйте STATIC файлы:
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
### API ресурсы:
- **AUTH**: Аутентификация.
- **USERS**: Пользователи.
- **TITLES**: Произведения, к которым пишут отзывы.
- **CATEGORIES**: Категория произведений ("Фильмы", "Книги", "Музыка").
- **GENRES**: Жанры, одно из произведений может быть присвоено к нескольким жанрам.
- **REVIEWS**: Отзывы на произведения.
- **COMMENTS**: Комментарии к отзывам.

### Примеры запросов:

Пример GET запроса:
```
GET http://51.250.16.72/api/v1/genres
```
Ответ:
```
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": 0,
        "name": "string",
        "year": 0,
        "rating": 0,
        "description": "string",
        "genre": [
          {
            "name": "string",
            "slug": "string"
          }
        ],
        "category": {
          "name": "string",
          "slug": "string"
        }
      }
    ]
  }
]
```
Пример POST запроса:
```
POST http://51.250.16.72/api/v1/titles/{title_id}/reviews/
```
Содержимое запроса:
```
{
  "text": "string",
  "score": 1
}
```
Ответ:
```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 1,
  "pub_date": "2019-08-24T14:15:22Z"
}
```


### Автор:
Sakov Dmitry

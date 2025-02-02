# fitcypher
Health and Fitness Tracker

[FitCypher Blog](https://alexlaverty.github.io/categories/fitcypher/)

## Create Super User 

User who can access the admin dashboard

```
python manage.py createsuperuser

python manage.py createsuperuser
Username : admin
Email address: admin@admin.com
Password: admin
Password (again): admin
Superuser created successfully.
```

## Run FitCypher in Docker container

```
docker build -t fitcypher .
docker run -p 8000:8000 fitcypher
```

## REST API 

```
curl -X POST http://127.0.0.1:8000/api/entries/ \
-H "Content-Type: application/json" \
-u your_username:your_password \
-d '{
    "date": "2023-10-15T12:00:00Z",
    "tracking": "weight",
    "numerical_value": 70.5,
    "notes": "After breakfast",
    "tags": "morning",
    "source": "fitcypher"
}'
```
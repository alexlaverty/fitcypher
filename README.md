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
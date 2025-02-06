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

### GET

Export your entries via the rest API

```
curl -X GET http://127.0.0.1:8000/api/entries/ \
-H "Content-Type: application/json" \
-u your_username:your_password
```
### POST

Create entries via the rest api
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

### POST

Create entries via the rest api
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

or post multiple entries with batch post :

```
curl -X POST http://127.0.0.1:8000/api/entries/batch/ \
-H "Content-Type: application/json" \
-u your_username:your_password \
-d '[{
    "id": 1,
    "user": {
        "id": 1,
        "username": "alex"
    },
    "date": "2023-10-15T12:00:00Z",
    "tracking": "food",
    "string_value": "Banana and Porridge",
    "numerical_value": null,
    "notes": "",
    "tags": "",
    "source": "fitcypher"
}, {
    "id": 2,
    "user": {
        "id": 1,
        "username": "alex"
    },
    "date": "2025-02-02T04:56:52.968347Z",
    "tracking": "exercise",
    "string_value": "raised arm circles",
    "numerical_value": "8.00",
    "notes": "Video ID: g3oaRLbo-yw",
    "tags": "darebee",
    "source": "youtube"
}]'
```

## Extract Youtube Channel Video ID's to JSON 

```
pip install yt-dlp
yt-dlp --flat-playlist --print "%(id)s,%(title)s,%(duration)s" "https://www.youtube.com/playlist?list=PLz-l7oWFJS0Lyvvb-m0YzEjAmtcezXCki" 2>/dev/null | awk -F',' '{gsub(/"/, "\\\""); print "{\"id\":\"" $1 "\", \"title\":\"" $2 "\", \"duration\":\"" $3 "\"}"}' | jq -s '.' > opex-core.json
```
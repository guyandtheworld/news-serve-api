# apis

## Instructions

### This needs to be dockerized.

- Create and activate a `virtualenv`
- `pip install -r requirements.txt`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py createsuperuser` - make a user for logging into admin panel
- `python manage.py runserver`

All URLs for the API can be found at `/apis/urls.py`.

All APIs consume a JSON object in a POST request.
The key from the JSON data is passed to `getSingleObjectFromPOST()` or `getManyObjectsFromPOST()`. So check these functions in `/apis/views.py` to find out what should be the key in the JSON data for a particular endpoint.

Populate the database through Django Admin.

### API Flow

* POST to - `/api/apiauth`
```
  {
	"username": "dev",
	"password": "alrtai2019"
  }

Content-Type: application/json
```
* POST to - `/api/getclientname`

```
{
	"uuid": "e6b263da-9789-4ecb-956f-93af17ed959a" # user uuid
}
Authorization: Token 9923488b8dd78a1fe99c2389be498c122688f2c7
Content-Type: application/json
```

## Development
  * `docker-compose -f docker-compose-dev.yml run apis python manage.py migrate`
  * `docker-compose -f docker-compose-dev.yml run apis python manage.py createsuperuser`
  * `docker-compose -f docker-compose-dev.yml  up --build`

## Production

* `docker-compose -f docker-compose-prod.yml up --build`


### Issues
* `Allowed-Hosts` has to be set to restrict incoming request origins.
* use cloudflare for HTTPS serving
* disable CORS

### Database


Read only access.

`GRANT SELECT ON ALL TABLES IN SCHEMA public TO xxx;`
`ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO xxx;`


### Resources
* [DRF Prod](https://dragonprogrammer.com/django-drf-api-production-docker/)
* [Understanding uwsgi, threads, processes, and GIL](https://www.reddit.com/r/Python/comments/4s40ge/understanding_uwsgi_threads_processes_and_gil/)
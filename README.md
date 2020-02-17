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

### Issues

- The password is currently just a `CharField`. Would be great if someone could implement hashing and other auth related things.
- It just uses the default SQLite db for now.
- It will accept requests from any client now. `Allowed-Hosts` has to be set to restrict incoming request origins.

# news-serve-API

This repository contains all of the APIs which we serve to the end-user using our react.js dashboard. For running this repository, there are two methods. You could run it in development mode and you can run it in production. All you need to do put a new feature or a new API in production can be summarized in small steps.

1. Clone this repository to your local machine.
2. Checkout a branch to get started on your feature.
3. Push your branch (NEVER DIRECTLY TO THE MASTER BRANCH) to the remote
4. Do a pull request to the master
5. Once the pull request is merged, the feature would be automatically deployed in Google Cloud Run.


## Installation.


1. Clone this repository `git clone https://github.com/guyandtheworld/news-serve-api`
2. Setup the Database Keys locally. 
    - Create a folder called `.keys` in the apis folder
    - Create a file called django.env in the `.keys` folder
    - Run `docker-compose -f docker-compose-prod.yml up --build` for local development
    - Get into the app container by running `docker exec -it <ID> bash`
    - Run migrations using `python manage.py migrate`
    - Put the db credential in the file (ask Adarsh)
    - Run `docker-compose -f docker-compose-prod.yml up --build` for production
    - Go to `http://localhost:8000/`
    - If you can see a alrt API page with URLs, you've been successful.
    - You can visit `http://localhost:8000/admin` to see all of our models and data we have in our database (Remote Google Cloud SQL)


### Additionally, if you want to develop quickly. (Recommended)
* Install [Virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) locally
* Create an environment within apis folder `python3 -m venv env`
* Activate the virtual environment `source env/bin/activate`
* Install the packages our server needs `pip install -r requirements.txt`
* Input the following credentials into you `.bashrc` file. (Get actual values from Adarsh)
    ```
    export SECRET_KEY="xxxx"
    export DB_NAME=xxxx
    export DB_USER=xxxx
    export DB_PASSWORD=xxxx
    export DB_HOST=xxxx
    export DB_PORT=xxx
    export DJANGO_SETTINGS=prod
    ```
* Reload your terminal and activate virtual environment again. (Do this step each time you're developing)
* Run `python manage.py runserver` to see your server running locally at `http://localhost:8000/`
* If you can see a alrt API page with URLs, you've been successful.
* You can visit `http://localhost:8000/admin` to see all of our models and data we have in our database (Remote Google Cloud SQL)


## Development

### Before Starting Development

* Before writing a new feature, checkout a new branch on git: `git checkout -b <BRANCH NAME>`
* After writing and testing feature: `git add .` and `git commit -m "<PROPER COMMIT MESSAGE>"`
* Push to YOUR BRANCH: `git push origin <BRANCH NAME>`. Never push to master. It will get deployed.

### Updating your local branch

Before any development, to ensure your branch is up-to-date with the master. You need to:
* `git fetch origin` Get all changes in the remote repository
* `git rebase origin/master` Make sure all changes in the remote is reflecting in your locally.


We run our server in a docker-container. So each time you finish a feature. You need to run `docker-compose -f docker-compose-prod.yml up --build` and visit `http://localhost:8000/admin` to test if the API is working.

For that I recommend installing [Insomnia](https://insomnia.rest/) application to test your API out. 


### Testing the APIs

Everything you do through the APIs can be done easily through the Django `/admin`. And while the server is running in the background:

* Step 1: Set header
![Set Header](https://i.imgur.com/GtTWd4p.png)

* Step 2: Create your own user
![Create a user](https://i.imgur.com/fthWaTh.png)


* Step 3: Login and fetch user Token and User UUID
![Login](https://i.imgur.com/l36VdKP.png)
![User ID](https://i.imgur.com/vY6RFcG.png)

You will use token and UUID for all the other API calls

* Step 4: Choose any API from `http://localhost:8000/`
For example, we'll choose `/user/getclientname`. 

Set up the headers
![Headers](https://i.imgur.com/HmwueMH.png)


Pass in the unique ID of the User to get his client name.
![URL](https://i.imgur.com/irIewKd.png)


### Directory Structure

Django apps have 2 main components:
1. urls.py
2. views.py

All URLs for the API can be found at `/<app>/urls.py`.
All APIs consume a JSON object in a POST request.
The key from the JSON data is passed to `getSingleObjectFromPOST()` or `getManyObjectsFromPOST()`. So check these functions in `/apis/views.py` to find out what should be the key in the JSON data for a particular endpoint.

When writing a new API
* Define the URL in urls.py
* write the corresponding view at views.py

That's it! Sometimes, you might need to use a serializer or external utilities or sql queries. We have files dedicated to each application for that.

Our application has 5 main apps and 1 master app. `/alrtai` is the master app which contains all the settings for our server, url patterns etc.

Our other apps are:

* apis: all models, authentication (login, sign-up), user details APIs
* entity: contains APIs for entity (company) creation, listing etc
* feed: contains queries and APIs for generating and scoring feeds
* score: APIs and queries for generating scores for companies and buckets
* viz: visualizations for different entities and buckets


### After writing features
- Run `docker-compose -f docker-compose-prod.yml up --build` for production
- Go to `http://localhost:8000/`
- Test with Insomnia if your API is working as intended. If it is, push to YOUR BRANCH.


### Making changes to database
Suppose you want to make a change to our database like add a new table or edit an attribute. Go to `apis/models/` and choose which directory your model is in. Make respective changes. and run these commands.

* `python manage.py makemigrations`: Converts your python code to files.
* `python manage.py migrate`: Writes your changes to the database

This way, you never have to interact with the models manually.

### Miscellaneous
* `python manage.py createsuperuser` - make a user for logging into admin panel


### Issues
* `Allowed-Hosts` has to be set to restrict incoming request origins.
* use cloudflare for HTTPS serving
* disable CORS

### Database

Read only access.
`GRANT SELECT ON ALL TABLES IN SCHEMA public TO xxx;`
`ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO xxx;`


### Resources
* [Django Short Tutorial](https://tutorial.djangogirls.org/en/)
* [DRF Prod](https://dragonprogrammer.com/django-drf-api-production-docker/)
* [Understanding uwsgi, threads, processes, and GIL](https://www.reddit.com/r/Python/comments/4s40ge/understanding_uwsgi_threads_processes_and_gil/)

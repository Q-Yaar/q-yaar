# q-yaar
Get out to play.

## ***Project Specs***
* Ubuntu 22.04 (Preferred)
* Python - 3.11.9
* Django - 5.0.7
* Postgres - 18.1
* Docker - Follow the [link](https://docs.docker.com/get-docker/)
* Docker Compose - Follow the [link](https://docs.docker.com/compose/install/)
* Redis

## ***Setup on Local***

### Setup Postgres
```bash
$ sudo su - postgres 
$ psql -p 5434 # (Or whichever port runs your postgres 16.3) This will open psql shell, follow these commands

CREATE DATABASE q_yaar_db;
CREATE USER q_yaar_user WITH PASSWORD 'q_yaar_password';
ALTER ROLE q_yaar_user SET client_encoding TO 'utf8';
ALTER ROLE q_yaar_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE q_yaar_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE q_yaar_db TO q_yaar_user;
ALTER ROLE q_yaar_user SUPERUSER;
ALTER ROLE q_yaar_user CREATEDB;
```
Connect to DB from command line using psql
```bash
psql -d postgres://q_yaar_user:q_yaar_password@localhost:5434/q_yaar_db # Use the applicable port number
```

### Create a Virtual Environment
Make sure you're in the directory - q-yaar
```bash
$ python3 -m venv .venv  # This will create a virtual environment
$ source .venv/bin/activate  # You can see the virtual environment is active
$ cd q_yaar_platform
$ pip install -r requirements.txt # This will install all the requirements
```

### Setup .env File
Make sure you're in the directory - q_yaar_platform
```bash
$ touch .env
```
Now copy and paste the contents available in the file - env_example <br />
Ask someone for the actual env values

### Setup Docker and Start Redis Server
Start a Redis container:
```bash
$ docker run -d --name redis -p 6379:6379 redis:7.4-alpine
```
*(Make sure the port matches your `REDIS_URL` in `.env`)*

If you want to stop the Redis server:
```bash
$ docker stop redis
```

### Run the Django Server
Make sure you're in the directory - q_yaar_platform

```bash
$ python manage.py migrate
$ python manage.py runserver
```
You should see your server running on __127.0.0.1:8000__ 

### Create a Superuser to get Admin Access
Make sure you're in the directory - q_yaar_platform
```bash
$ python manage.py createsuperuser
```
Follow the instructions on the screen to create a superuser <br />
Ensure that you enter a valid uuid during superuser creation

### Try logging into admin
Open the following url in your browser - __127.0.0.1:8000/admin/__ <br />
Login using the username and password entered during superuser creation <br />
You can now access all the models through django admin

## ***Formatting***
Use black (already mentioned in requirements.txt) <br />
Make sure the line length arg is set to 119 (it defaults to 80 if nothing is set)

* For VScode, add the below configs to your settings.json file

```
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.languageServer": "Pylance",
    "python.formatting.provider": "black",
    "python.linting.flake8Args": [
        "--max-line-length=119"
    ],
    "python.formatting.blackArgs": [
        "--line-length=119"
    ],
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    },
    "black-formatter.args": [
        "--line-length",
        "119"
    ],
    "python.autoComplete.extraPaths": [],
    "python.analysis.extraPaths": [
        "q_yaar_platform"
    ]
}
```

### Running dev server with Docker
Ensure environment configuration is present in `build_meta/.env_dev` (refer to `q_yaar_platform/env_example`).

From the project root, run the deployment script:
```bash
$ sh docker/deploy.sh dev
```
*(Or navigate to `docker/` and run `sh deploy.sh dev`)*

To create a superuser inside the container:
```bash
$ docker exec -it dev-django python manage.py createsuperuser
```
*(Or get a shell inside the container using `docker exec -it dev-django /bin/bash`)*

## ***Running the Staging/Production Server***

1. SSH into the instance using the provided creds.
2. cd into the docker directory and run the unified deployment script with the desired target environment (`staging` or `prod`):
```bash
$ cd q_yaar_backend/q-yaar/docker
$ sh deploy.sh staging
# or for production:
$ sh deploy.sh prod
```

Available script options:
* `--no-pull` : Do not pull latest changes from git
* `--collectstatic` : Run `python manage.py collectstatic --noinput` inside the container

For example, to deploy staging and collect static assets:
```bash
$ sh deploy.sh staging --collectstatic
```

3. [OPTIONAL] If you get KeyError: 'ContainerConfig', delete that container and re-run the deployment script:
```bash
$ sudo docker ps -a
$ sudo docker stop <container_id>
$ sudo docker rm <container_id>
$ sh deploy.sh staging
```

NOTE: Option 3 needs to be fixed on the server by updating docker. #TODO.

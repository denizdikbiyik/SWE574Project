# SWE574 Course Project - CommUnity

This repository is created for SWE574 project. This is a group project.

## CommUnity

To run the system locally, the project should be cloned from the following repository: https://github.com/denizdikbiyik/SWE574Project There should be an IDE like Visual Studio Code to open the project and a database software to open PostgreSql like pgAdmin. Docker Desktop should also be installed because docker commands cannot be run without it. 

To create the virtual environment for the project, run the following command:
```python3 -m venv myvenv``` Then, to activate the virtual environment run the command below on the project directory in the terminal. It changes according to your operating system: For mac: ```source myvenv/bin/activate``` For windows: ```myenv/Scripts/activate``` All the requirements should be installed to use the system. The needed installations are given in the requirements.txt file, so just by run the following command: ```pip install -r requirements.txt```

Env file should also be configured to use the system. Update the file like below. Also a template for env file is given in the project with the name .env example. The DB_HOST part should have the db command open there which is configured for Docker. To run the system locally with a local postgresql database, localhost could be given there. 

```DJANGO_SECRET_KEY='your django key comes here'```

```DJANGO_DEBUG=True```

```DJANGO_ALLOWED_HOSTS="0.0.0.0"```

```POSTGRES_HOST_AUTH_METHOD=trust```

```DB_ENGINE=django.db.backends.postgresql_psycopg2```

```#DB_NAME=CommUnitySocial```

```DB_NAME=communitysocial```

```DB_USER=postgres```

```DB_PASSWORD=admin```

```#DB_HOST=localhost```

```DB_HOST=db```

```DB_PORT=5432```

```CORS_ALLOWED_ORIGINS="http://localhost:3000 http://127.0.0.1:3000"```


If you will run the system without docker, DB_NAME part can have CommUnitySocial, but for Docker, it should be communitysocial. 

To create the database for Docker, some commands should also be run. Firstly, create a database on your local machine. Run the following command to build the Docker images: ```docker-compose up --build``` Then, to start the database: ```docker-compose start db``` Because the db is defined as core_db, run the following command: ```docker exec -it core_db bash``` The creation process should be started by the following: ```psql -U postgres``` Database should be created: ```CREATE DATABASE communitysocial;``` Run the following commands: ```\l```, ```\q``` You can exit from there by typing: ```exit``` Run the images for Docker: ```docker-compose up``` If you want it to run on the background: ```docker-compose up -d``` The system can be reachable from http://127.0.0.1:80/ link. The “python manage.py runserver” command is not needed to be run because it is written in the Dockerfile. All needed commands to do migrations for the database are also written there.
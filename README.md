# SWE573 Course Project - CommUnity

This repository is created for SWE573 project. The project owner is Deniz Dikbıyık.

## CommUnity

This web project is for people to be able to offer some services to the other people and also be able to take them. System will match the takers and receivers and get feedback after the service is delivered. Users will spend credit hours when they attend any offer, and earn credit hours when they give services.

There will be also an event option to make people meet and share some funny time.

To get the source code on your local machine, you can use 
```git init``` command, and then ```git clone https://github.com/denizdikbiyik/SWE573Project``` command.

To run the system locally, there should be an ide to open the code like Visual Studio code and PostgreSql for the database. Docker desktop should also be installed because docker commands cannot be run without it. To create the virtual environment for the project, ```source myvenv/bin/activate``` command should be run on the project directory in the terminal. All the requirements should be installed to use the system. The needed installations are given in the requirements.txt file, so just by running ```pip install -r requirements.txt``` command, the process can be completed. Env file should also be configured to use the system. Update the file like below. Also a template for env file is given in the project with the name .env example.

```DJANGO_SECRET_KEY='your django key comes here'```

```DJANGO_DEBUG=True```

```DJANGO_ALLOWED_HOSTS="0.0.0.0"```

```POSTGRES_HOST_AUTH_METHOD=trust```

```DB_ENGINE=django.db.backends.postgresql_psycopg2```

```DB_NAME=communitysocial```

```DB_USER=postgres```

```DB_PASSWORD=admin```

```#DB_HOST=localhost```

```DB_HOST=db```

```DB_PORT=5432```

```CORS_ALLOWED_ORIGINS="http://localhost:3000 http://127.0.0.1:3000"```

The DB_HOST part should have the db command open there which is configured for Docker. To run the system locally with a local postgresql database, localhost could be given there. To create the database for Docker, some commands should also be run. Firstly, create a database on your local machine. Run ```docker-compose up --build``` command to build the Docker images. Then, ```docker-compose start db``` should be run to start the db. After it, because the db is defined as core_db ```docker exec -it core_db bash``` should be run. By ```psql -U postgres``` command, the creation process will be started and after writing ```\l``` , the command can be given as ```CREATE DATABASE communitysocial;``` there. You can exit from here by writing ```exit``` two times.
To run the images for Docker, ```docker-compose up``` should be run. If you want the run to be continued in the background, you can run the ```docker-compose up -d``` command. 

The system also has an admin side. So, to create an admin user, please run the command ```python manage.py createsuperuser```.

The system can be reachable from http://127.0.0.1:80/ link. The “python manage.py runserver” command is not needed to be run because it is written in the Dockerfile. All needed commands to do migrations for the database are also written there.
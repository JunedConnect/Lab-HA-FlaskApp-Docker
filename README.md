# Deploying a Highly Available Flask App with Redis using Docker

<br>

## Overview

In this guide, you will set up a simple Flask web application that uses Redis to store visit attempts. The setup includes:

- **Two Flask Application Servers**: Each Flask app will interact with Redis to track the number of visits.
- **Redis Database**: A Redis container will store the visit count.
- **Nginx Load Balancer**: Distributes incoming traffic between the Flask application servers.
- **Docker Compose**: To easily orchestrate the entire setup with a single command.

By the end of this guide, you will have a fault-tolerant web app with automatic load balancing and a shared Redis database for tracking visit counts.

## Project Setup

Your project folder should have the following structure:

```
├── flask-app (directory)
│   ├── app.py
│   └── Dockerfile
├── redis-volume-data (directory)
├── nginx (directory)
│   └── nginx.conf
├── docker-compose.yml
```

Each of these folders and files will be set up to work together using Docker. Ensure that you have this same structure when following the guide below.

## Step 1: Flask Application Setup

### 1.1 Create Flask Application (app.py)

When users visit the app, they’ll be able to view the visit count, which is stored in Redis. The **app.py** file sets up two routes: one for the homepage (`/`) and one for the visit count (`/count`). The visit count is retrieved from Redis, and every time someone visits the `/count` route, the count increments.

```
import os
import time
from redis import Redis
from flask import Flask

redis_port = os.getenv('redis_port')
app = Flask(__name__)
redis = Redis(host='redis', port=redis_port)

@app.route("/")
def home():
    html = """
    <html>
    <head>
        <title>Welcome</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4; }
            h3 { color: #333; }
            .button {
                background-color: #008CBA;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                font-size: 16px;
                margin-top: 20px;
                cursor: pointer;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
            }
            .button:hover { background-color: #005f75; }
        </style>
    </head>
    <body>
        <h3>Hi there, Visitor!</h3>
        <p>Welcome to the page. Click below to see the visit count.</p>
        <a class="button" href="/count">Go to Visit Count</a>
    </body>
    </html>
    """
    return html

@app.route("/count")
def count():
    visits = redis.incr('counter')
    html = f"""
    <html>
    <head>
        <title>Visit Count</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f4f4f4; }}
            h3 {{ color: #333; }}
            .button {{
                background-color: #008CBA;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                font-size: 16px;
                margin-top: 20px;
                cursor: pointer;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
            }}
            .button:hover {{ background-color: #005f75; }}
        </style>
    </head>
    <body>
        <h3>Visit Count</h3>
        <p>This page has been visited {visits} times.</p>
        <a class="button" href="/">Go Back</a>
    </body>
    </html>
    """
    return html

flask_port = os.getenv('flask_app_port')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=flask_port)
```

### 1.2 Create Dockerfile

The **Dockerfile** specifies how to package your Flask app into a Docker container. It installs the required dependencies (Flask and Redis) and sets up the application to run within the container. This step ensures that your Flask app can be easily deployed using Docker.

```
FROM python:3.8-slim

WORKDIR /app

RUN pip install flask redis

COPY . .

CMD ["python", "app.py"]
```

Here’s a quick breakdown of the file:

- **Base Image**: The `FROM` command specifies the base image (Python 3.8) that the container will use. This provides a minimal environment with Python installed.
- **Set Working Directory**: The `WORKDIR` command sets the working directory inside the container to `/app`. This is where all your app's files will be placed and where commands will be run.
- **Install Dependencies**: The `RUN` command is used to install the necessary Python packages (`Flask` for the web app and `Redis` for interacting with the Redis database).
- **Copy Files**: The `COPY` command copies all the project files within the current folder (i.e `app.py`) from your local machine into the container's `/app` directory.
- **Run the App**: The `CMD` command tells Docker to run your Flask app (`app.py`) when the container starts.

<br>

<br>

Ensure that both files (**app.py** and **Dockerfile)** are placed within the flask-app directory.

<br>

## Step 2: Setting Up Nginx Load Balancer

### 2.1 Create Nginx Configuration (nginx.conf)

The **nginx.conf** file is used to configure Nginx for load balancing between the two Flask servers. It forwards all requests to the primary Flask app, and if that’s unavailable, it uses the backup Flask app. This ensures that your application remains available even if one Flask server goes down, making it fault-tolerant.

```
user  nginx;
events {
    worker_connections   1000;
}

http {
    upstream backendserver {
        server flask:5000;
        server flaskbackup:5001 backup;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backendserver/;
        }
        location /count {
            proxy_pass http://backendserver/count;
        }
    }
}
```

<br>

<br>

This **nginx.conf** file should be placed within the nginx directory.

<br>

## Step 3: Docker Compose Configuration

The **docker-compose.yml** file orchestrates the Redis, Flask, and Nginx services.

```
services:
  redis:
    image: redis:8.0-M03-alpine
    container_name: redis
    ports:
      - 6379:6379
    command: redis-server --port 6379
    volumes:
      - ./redis-volume-data:/data

  flask:
    build: ./flask-app/
    container_name: flask-app
    ports:
      - 5000:5000
    depends_on:
      - redis
    environment:
      - redis_port=6379
      - flask_app_port=5000

  flaskbackup:
    build: ./flask-app/
    container_name: flask-app-backup
    ports:
      - 5001:5001
    depends_on:
      - redis
    environment:
      - redis_port=6379
      - flask_app_port=5001

  nginxloadbalancer:
    image: nginx:1.27.4-alpine
    container_name: nginx
    ports:
      - 80:80
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - flask
      - flaskbackup
```

Here’s a quick breakdown of the file, it runs 4 services:

- **Redis**: Runs a Redis server on port 6379 and stores its data persistently in a local directory.
- **Flask (Primary)**: Built from Dockerfile in step 1, it runs on port 5000 and depends on Redis for data storage.
- **Flask (Backup)**: A backup Flask app, built the same way, running on port 5001, and also depends on Redis.
- **Nginx**: Acts as a load balancer, distributing traffic between the two Flask apps.

<br>

<br>

This **docker-compose.yml** file should be placed within the root project directory.

<br>

## Step 4: Running Docker Compose

### 4.1 Navigate to the Project Directory and start the containers

Ensure you are in the root directory of your project (where **docker-compose.yml** is located) within your CLI:

```
cd /path/to/your/project
```

Then run the following command to start the entire stack:

```
docker-compose up --build
```

### 4.2 Verify the Application

Once everything is up, navigate to `http://localhost` in your browser. You should see the homepage of the Flask app. Click on the link to the "Visit Count" page to see the total visit count.

### 4.3 Stop the Containers

To stop all running containers, use the following command:

```
docker-compose down
```

## And that's it. Done!

You now have a simple but scalable setup for your Flask web app, using Redis for state persistence and Nginx for load balancing. You can adjust the number of Flask containers or modify Nginx's settings as needed for higher availability.

|Here’s what it will look like (mine will have a different layout as I had customised the app.py script in Step 1):|
|-------|
| ![WebServer1](https://raw.githubusercontent.com/JunedConnect/Lab-HA-FlaskApp-Docker/main/images/Flask%20App%201.png) |
| ![WebServer1](https://raw.githubusercontent.com/JunedConnect/Lab-HA-FlaskApp-Docker/main/images/Flask%20App%202.png) |

## Overview
> [!NOTE]
> This repository contains a personal project designed to enhance my skills in software engineering. It focuses on developping an API that will periodically retrieve feed data into itself from ArXiv via OAI (open archive initiative). Data is stored inside a Mongo database. The API is accessed 

> [!IMPORTANT]
> Many architectural choices and decisions in this project may not make the most efficent sense on purpose for the sake of practicing and learning.

## Architecture 
This project showcases a comprehensive Dockerized environment for running a web application stack. It includes services for MongoDB, a Python Cron job, a web server with NGINX, and a Flask API. The configuration is orchestrated using Docker Compose, making it easy to deploy and manage.

#### MongoDB Service
The MongoDB service runs the MongoDB database with authentication enabled. It uses environment variables for configuration, allowing flexibility in setting the root username, root password, and initial database. Data persistence is ensured by mounting a volume, and the service is connected to the backend network.

#### Python Cron Service
The Python Cron service is responsible for scheduled tasks and jobs. It utilizes a Docker image built from the provided Dockerfile. The service is configured with UTC timezone and logs are maintained in a separate volume. It depends on the MongoDB service and is connected to the backend network. The code used is the same as the entire project.

#### Web Server with NGINX
The web server service uses NGINX to serve the application. It is built from a Dockerfile and configured for production. The service exposes ports 80 and 443, making the application accessible through HTTP and HTTPS. Log data is stored in a dedicated volume, and it depends on the Flask API service. This service is connected to the frontend network.

#### Flask API
The Flask API service provides the core application functionality. It is built from a Dockerfile and configured with environment variables for various settings, including the MongoDB connection details. The service is exposed on port 5000 and depends on the MongoDB service. It is connected to both the frontend and backend networks.

## Diagram
![Diagram](diagram.png)

## Getting started
### Prerequisites

### Installation

This Docker Compose configuration facilitates a modular and scalable deployment whether you are developing, testing, or deploying a production environment.

https://dotmobo.github.io/celery.html
https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#celerytut-configuration
https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
http://export.arxiv.org/oai2?verb=ListRecords&from=2023-11-08&set=cs&metadataPrefix=oai_dc

https://www.digitalocean.com/community/tutorials/how-to-set-up-flask-with-mongodb-and-docker#step-2-writing-the-flask-and-web-server-dockerfiles
https://github.com/digitalghost-dev/premier-league/tree/main
https://github.com/othneildrew/Best-README-Template

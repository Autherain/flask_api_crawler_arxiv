# Overview
> [!NOTE]
> This repository contains a personal project designed to enhance my skills in software engineering. It focuses on developping an API that will periodically retrieve feed data into itself from ArXiv via OAI (open archive initiative). Data is stored inside a Mongo database. The API is accessed through nginx. 

> [!IMPORTANT]
> Many architectural choices and decisions in this project may not make the most efficent sense on purpose for the sake of practicing and learning.

## Built with 
* Lazydocker
* LazyVim
* Excalidraw
* Docker
* Python

# Getting started
### Prerequisites
* Docker

### Installation
1. Clone the repo 
```sh
https://gitlab-student.centralesupelec.fr/etienne.vaneecloo/flask_api_crawler_arxiv.git
```
2. Switch to where the docker compose file is 
```
cd flask_api_crawler_arxiv/src/flask_api_crawler_arxiv
```
3. Spin up the project 
```
docker compose build && docker compose up
```
4. Get the the API IP 
```
docker inspect $(docker ps -aqf "name=webserver") | grep "IPAddress"
```

# Endpoint Comments

## `/articles/` - GET
- **Description:** Endpoint to retrieve paginated articles.
- **Parameters:**
  - `page` (optional): Page number for pagination (default is 1).
- **Returns:** Paginated articles in JSON format.

## `/article/<id>` - GET
- **Description:** Endpoint to retrieve an article by its ID.
- **Parameters:**
  - `id` (str): ObjectId of the article.
- **Returns:** Article details in JSON format.

## `/text/<id>.txt` - GET
- **Description:** Endpoint to retrieve the summary of an article by its ID.
- **Parameters:**
  - `id` (str): ObjectId of the article.
- **Returns:** Article summary in JSON format.

## `/articles` - POST
- **Description:** Endpoint to insert a new document from the user.
- **Request Body:**
  - JSON document with keys `header` and `metadata`.
- **Returns:**
  - Success message with the inserted document ID in JSON format.
  - Error message in case of validation failure or other errors.

## `/time` - GET
- **Description:** Returns the current server time.

## `/health` - GET
- **Description:** Health check endpoint returning "OK".

## `/` - GET
- **Description:** Welcome message endpoint.

## `/version` - GET
- **Description:** Returns the version information of the Flask API and Python.

## `/umad_bra` - GET
- **Description:** ASCII art representation.


## Diagram
![Diagram](diagram.png)

## Architecture 
This project showcases a comprehensive Dockerized environment for running a web application stack. It includes services for MongoDB, a Python Cron job, a web server with NGINX, and a Flask API. The configuration is orchestrated using Docker Compose, making it easy to deploy and manage.

#### MongoDB Service
The MongoDB service runs the MongoDB database with authentication enabled. It uses environment variables for configuration, allowing flexibility in setting the root username, root password, and initial database. Data persistence is ensured by mounting a volume, and the service is connected to the backend network.

#### Python Cron Service
The Python Cron service is responsible for scheduled tasks and jobs. It utilizes a Docker image built from the provided Dockerfile. The service is configured with UTC timezone and logs are maintained in a separate volume. It depends on the MongoDB service and is connected to the backend network. The code used is the same as the entire project.

#### Web Server with NGINX
The web server service uses NGINX to serve the application. It is built from a Dockerfile and configured for production. The service exposes ports 80 and 443, making the application accessible through HTTP and HTTPS. Log data is stored in a dedicated volume, and it depends on the Flask API service. This service is connected to the frontend network.

#### Flask API
The Flask API service provides the core application functionality. It is built from a Dockerfile and configured with environment variables for various settings, including the MongoDB connection details. The service is exposed on port 5000 and depends on the MongoDB service. It is connected to both the frontend and backend networks. It uses gunicorn with 4 workers to 

## Acknowledgments
* https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#celerytut-configuration
* https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
* http://export.arxiv.org/oai2?verb=ListRecords&from=2023-11-08&set=cs&metadataPrefix=oai_dc
* https://www.digitalocean.com/community/tutorials/how-to-set-up-flask-with-mongodb-and-docker#step-2-writing-the-flask-and-web-server-dockerfiles
* https://github.com/digitalghost-dev/premier-league/tree/main
* https://github.com/othneildrew/Best-README-Template


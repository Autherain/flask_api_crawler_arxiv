FROM python:3.8

ENV PYTHONPATH=/app
# Install cron and other necessary tools
WORKDIR /app

#The context appear inside the docker compose file. 
COPY . /app/flask_api_crawler_arxiv

RUN apt update && \
  apt install -y cron && \
  rm -rf /var/lib/apt/lists/* && \
  mv /app/flask_api_crawler_arxiv/python_cron/cronjob /etc/cron.d/cronjob && \
  chmod 0644 /etc/cron.d/cronjob && \
  pip install -r /app/flask_api_crawler_arxiv/requirements.txt && \
  crontab /etc/cron.d/cronjob

# Run the cron job and keep the container running
ENTRYPOINT ["cron", "-f", "-L", "/dev/stdout"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]

FROM python:3.10.0
WORKDIR /app
ARG SECRET_KEY
ARG ALLOWED_HOSTS
ENV SECRET_KEY=${SECRET_KEY}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
COPY requirements.txt .
RUN apt-get update && apt-get install -y netcat
RUN pip install -r requirements.txt
COPY . .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
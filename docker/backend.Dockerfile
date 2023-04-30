FROM python:3.8.13-slim

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY docker/nginx-be.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# CV dependencies
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install tesseract-ocr -y

# copy source and install dependencies
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/backend
COPY ./requirements.txt /opt/app/
COPY ./docker/start-server.sh /opt/app/
COPY receipt /opt/app/backend/
WORKDIR /opt/app
RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app

# start server
EXPOSE 8080
CMD ["sh", "/opt/app/start-server.sh"]
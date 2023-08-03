# Select the base image from hub.docker
FROM python:3.9-alpine3.13
LABEL maintainer="Lcerenc"

# PYTHONUNBUFFERED => Allows to send the stouput and stderrror directly in the terminal
ENV PYTHONUNBUFFERED 1

# Copy requirements and app directory to the docker coontainer
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
# Create env and install requirements AND add user
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \  
    apk add --upgrade --no-cache postgresql-client && \
    apk add --upgrade --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Define ENV PATH for python
ENV PATH="/py/bin:$PATH"

# Change user to django-user
USER django-user



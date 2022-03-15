# Reference: https://fedoramagazine.org/create-containerized-machine-learning-model/

FROM python:3.9-slim-bullseye

# Copy the application folder inside the container
WORKDIR /app
COPY ../podman-movie-demo ./podman-movie-demo

RUN pip3 install -r ./podman-movie-demo/requirements.txt

EXPOSE 5000

ENTRYPOINT cd podman-movie-demo && python3 server.py

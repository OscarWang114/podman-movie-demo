# podman-movie-demo

## Installation
Reference: https://www.atlantic.net/dedicated-server-hosting/how-to-install-and-use-podman-on-ubuntu-20-04/

Install podman:
```bash
sudo apt-get update -y

sudo apt-get install curl wget gnupg2 -y

sudo source /etc/os-release
sudo sh -c "echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list"

wget -nv https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/xUbuntu_${VERSION_ID}/Release.key -O- | sudo apt-key add -

sudo apt-get update -qq -y
sudo apt-get -qq --yes install podman
```

Install dev dependencies:
```bash
pip install -r requirements.dev.txt
```

## Training a collaborative filtering model
Reference https://www.jiristodulka.com/post/recsys_cf/


Run `train_model.ipynb` to train the model and obtain
a prediction of top 10 movie ids for all 610 users, saved in `top_n_movie_ids.pkl`.

## Containerizing

### Single container

Build an image and run a container named `deployment` in the background:
```bash
podman build -t deployment .
podman run -d --name deployment -p 5000:5000 deployment
```

Test out the API:
```bash
curl localhost:5000/recommend/10
# should return 1204,898,1237,1262,1272,1196,50,112552,318,904
```

Perform simple load testing with Apache Bench (200 concurrent requests, 10000 requests in total)
```bash
# if not installed, run `sudo apt install apache2-utils`
ab -n 10000 -c 200 http://localhost:5000/recommend/10
```

Percentage results from Apache Bench:
```
Percentage of the requests served within a certain time (ms)
  50%    309
  66%    317
  75%    323
  80%    327
  90%    350
  95%    381
  98%   1325
  99%   1349
 100%   3360 (longest request)
```

Stop the container
```bash
podman stop deployment
```

### Two containers with a load balancer
Reference: https://notes.elmiko.dev/2020/12/27/messing-around-with-nginx-podman.html 


Create a podman network named `deployment_net`
```bash
podman network create deployment_net
```

Build an image and run two containers named `deployment1` and `deployment2` in the background. 
Specify `--network deployment_net` so the containers reside in the same network space:
```bash
podman build -t deployment .
podman run -d --name deployment1 --network deployment_net deployment
podman run -d --name deployment2 --network deployment_net deployment
```

Build and run the NGINX container to serve as the load balancer in the foreground:
```bash
podman run -v `pwd`/nginx.conf:/etc/nginx/nginx.conf:Z -p 5000:5000 \
--name nginx --network deployment_net docker.io/library/nginx

# If success, you should see "/docker-entrypoint.sh: Configuration complete; ready for start up"
```

Test out the API in another shell session:
```bash
curl localhost:5000/recommend/10
# should return 1204,898,1237,1262,1272,1196,50,112552,318,904
```

Perform a simple load testing with Apache Bench (200 concurrent requests, 10000 requests in total)
```bash
# if not installed, run `sudo apt install apache2-utils`
ab -n 10000 -c 200 http://localhost:5000/recommend/10
```

Percentage results from Apache Bench:
```
Percentage of the requests served within a certain time (ms)
  50%    218
  66%    232
  75%    240
  80%    245
  90%    257
  95%    269
  98%    287
  99%    305
 100%    360 (longest request)
```

Stop the containers
1. Press ctrl + c in the NGINX container's shell session
2. Stop the two other containers
```bash
podman stop deployment1
podman stop deployment2
```

## Troubleshooting

1. Problem: `Error: error creating container storage: the container name "<name>" is already in use by "<id>". You have to remove that container to be able to reuse that name.: that name is already in use`. Solution: do `podman rm --storage <id>` 
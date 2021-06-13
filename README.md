# ssci
Shit&amp;Sticks CI

Little tool to poll for changes in remote git repo, pull and run any commad after update.
docker and docker-compose are avaliable to use, if you need something else, feel free to use this as a base image.

Everything can be configured via env variables.

To run ssci use example docker-compose
```
version: "3.7"

services:
  ssci:
    image: mike0sv/ssci:latest
    restart: unless-stopped
    env_file:
      - template.env
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./repo:${PWD}/repo

 ```

 or this one-liner

 ```
 docker run --name ssci --restart=unless-stopped --env-file template.env -e HOST_DIR=$(pwd) -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/repo:$(pwd)/repo mike0sv/ssci:latest
 ```

 # Config envs

- HOST_DIR - used to replicate absolute repo path inside container, set it to `${PWD}` in env file for compose or to `$(pwd)` in docker run
- REPO_URL - git remote url to poll
- REPO_BRANCH - git branch, default master
- BUILD_CMD - command to run after each pull, for example `docker-compose up --build -d`
- TELEGRAM_TOKEN - telegram bot token to send notifications
- TELEGRAM_CHATS - comma-separated list of telegram chats

# Volumes

- /var/run/docker.sock - mount it, if you plan on using docker in your build cmd
- $(pwd)/repo:$(pwd)/repo - mount it, if your docker containers mount files from your repo
- anything mounted to /add will be copied into repo after pull

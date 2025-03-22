SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

# .PHONY is used to declare objectives that do not correspond to real files, but are tasks or 
# commands. This ensures that the task is always executed, even if make finds a file in the current
# directory with the same name as the task itself.

default: build

all:

# Manage go dependencies. Erase any unused dependency and copy go.mod dependencies to vendor/
deps:
	go mod tidy
	go mod vendor

# Compile the go package found at github.com/... and store the created binary at bin/client.
build: deps
	GOOS=linux go build -o bin/client github.com/7574-sistemas-distribuidos/docker-compose-init/client
.PHONY: build

# `-f`: used to specify the dockerfile location
# `-t`: is used to asign a tag to the created image. <image name>:<tag>
docker-image:
	docker build -f ./server/Dockerfile -t "server:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

# `up`: creates and starts the containers defined in the specified Compose file.
# `-d`: detached mode. Run the containers in the background as to not take over the terminal session.
# `--build`: force the rebuilding of the images before starting the containers.
docker-compose-up: docker-image
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up

# `stop`: stop running the containers, without removing them. This means that the containers can be
#         restarted later using `docker compose start`
# `-t 1`: specifies a 1-second timeout before forcefully stopping the containers (sends a SIGKILL)
# `down`: removes all containers, networks and volumes (unless marked as external). It completely
#         tears down the environment, requiring fresh container creation on the next `docker compose up`.

# Calling `stop` before `down` ensures a graceful shutdown (though redundant in most cases)
docker-compose-down:
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

# first `-f`: specifies the Compose file
# `logs`: display logs from all running containers defined in the Compose file
# second `-f`: follow. Used to keep streaming logs in real time
docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f --no-color
.PHONY: docker-compose-logs

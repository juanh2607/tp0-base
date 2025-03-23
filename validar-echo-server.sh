#!/bin/bash

# Config
SERVER_HOST="server"
SERVER_PORT=12345
MESSAGE="testing echo server"
# Docker prepends the name: to the network to create the network name. If name is not defined, it
# prepends the parent folder name.
# This can be overwritten with the `name:` tag within the `network:` tag
NETWORK_NAME="tp0_testing_net"

# echo $(docker network ls)

# Command breakdown:
#   * `docker run` executes a container based on an image.
#   * `--rm` automatically removes the container when execution ends.
#   * `--network` connects the container to the specified network.
#   * `busybox` is the image. A lightweigh linux image that includes netcat.
#   * `sh -c` indicates to execute the following string as a shell command in the container
#   * `nc` acts as a client, sending the message received through the pipe to the specified server and port
RESPONSE=$(docker run --rm --network "$NETWORK_NAME" busybox sh -c "echo '$MESSAGE' | nc '$SERVER_HOST' '$SERVER_PORT'")

if [ "$RESPONSE" = "$MESSAGE" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
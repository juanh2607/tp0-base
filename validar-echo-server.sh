#!/bin/bash

# Config
SERVER_HOST="server"
SERVER_PORT=12345
MESSAGE="testing echo server"
NETWORK_NAME="tp0-base_testing_net"

# Command breakdown:
#   * `docker run` executes a container based on an image.
#   * `--rm` automatically removes the container when execution ends.
#   * `--network` connects the container to the specified network.
#   * `busybox` is the image. A lightweigh linux image that includes netcat.
#   * `sh -c` indicates to execute the following string as a shell command in the container
#   * `nc` acts as a client, sending the message received through the pipe to the specified server and port
RESPONSE=$(docker run --rm --network "$NETWORK_NAME" busybox sh -c "echo '$MESSAGE' | nc '$SERVER_HOST' '$SERVER_PORT'")

if [[ "$RESPONSE" == "$MESSAGE" ]]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
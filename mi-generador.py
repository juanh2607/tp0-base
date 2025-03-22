import sys

# Parameters
output_file = sys.argv[1]
num_clients = int(sys.argv[2])

# - PYTHONUNBUFFERED=1. Ensure python output is sent immediately (for logging)
docker_compose = """services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net
"""

for i in range(1, num_clients + 1):
    client_service = f"""
  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i}
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
"""
    docker_compose += client_service


# testing_net: Isolated network that allow containers to communicate
# ipam: IP Address Management settings, used to configure the network
# driver: default. Use default IPAM driver to manage IP addresses
networks_section = """
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

docker_compose += networks_section

with open(output_file, "w") as f:
    f.write(docker_compose)

print(f"Archivo {output_file} generado exitosamente con {num_clients} clientes.")

import sys

# Parameters
output_file = sys.argv[1]
num_clients = int(sys.argv[2])

docker_compose = f"""name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      # Ensure python output is sent immediately (for logging)
      - PYTHONUNBUFFERED=1
      - CLIENTS={num_clients}
    networks:
      - testing_net
    volumes:
      # Mount config.ini from host machine to container
      - ./server/config.ini:/config.ini
"""

for i in range(1, num_clients + 1):
    csv_file = f"./.data/agency-{i}.csv"

    client_service = f"""
  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i}
    networks:
      - testing_net
    depends_on:
      - server
    volumes:
      # Mount config.yaml from host machine to container
      - ./client/config.yaml:/config.yaml
      - {csv_file}:/agency.csv
"""
    docker_compose += client_service


networks_section = """
networks:
  testing_net: # Isolated network that allow containers to communicate
    ipam: # IP Address Management settings, used to configure the network
      driver: default # Use default IPAM driver to manage IP addresses
      config:
        - subnet: 172.25.125.0/24
"""

docker_compose += networks_section

with open(output_file, "w") as f:
    f.write(docker_compose)

print(f"Archivo {output_file} generado exitosamente con {num_clients} clientes.")

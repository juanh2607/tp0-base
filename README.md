# Enunciado
### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. 
Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ 
(entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente 
antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso 
(hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

# Solución
Tanto en el cliente como en el servidor se genero una suscripción a la emisión de la señal `SIGTERM` y 
`SIGINT`.  
Tras la recepción de esta señal:
* El server finaliza el loop principal, cerrando el socket con el cuál recibe nuevas conexiones. Si
  había una conexión en proceso, se finaliza (dado que es enviar un solo mensaje).
* El cliente cierra su socket.

Ambos loggean la limpieza de recursos y el correcto cierre del proceso.

```
client1  | 2025-03-23 20:59:16 INFO     action: shutdown | result: success | client_id: 1
client1 exited with code 0
server   | 2025-03-23 20:59:16 INFO     action: shutdown | result: in_progress
server   | 2025-03-23 20:59:16 INFO     action: closing_listener | result: success
server   | 2025-03-23 20:59:16 INFO     action: shutdown | result: success
server exited with code 0
```

El flag `-t`, `--timeout` permite especificar el tiempo de espera antes de forzar el apagado del contenedor.
Este se encuentra en uso en el comando `make docker-compose-down`.
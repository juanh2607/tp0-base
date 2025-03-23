# Enunciado
### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `

# Solución

El script consiste principalmente del siguiente comando:
```sh
docker run --rm --network "$NETWORK_NAME" busybox sh -c "echo '$MESSAGE' | nc '$SERVER_HOST' '$SERVER_PORT'"
```

En términos generales, este comando crea un container que se conecta a la red `tp0_testing_net`, utilizando
la imágen `busybox` (la cuál contiene el comando `netcat`) y envía el mensaje al servidor, utilizando
el hostname y puerto de la red interna creada por docker (por lo que no se expone el puerto real).

Siendo más detallado, el comando está compuesto por las siguientes partes:
* `docker run` crea un contenedor basado en alguna imágen.
* `--rm` automáticamente elimina el contenedor una vez finaliza la ejecución.
* `--network` conecta al contenedor a la red especificada.
* `busybox` es la imágen a usar. Es una imágen ligera de Linux que incluye el comando `nc`.
* `sh -c` indica que se ejecute el string especificado como un comando de shell.
* `nc` actúa como un cliente, envíando el mensaje recibido desde el pipe al servidor especificado.
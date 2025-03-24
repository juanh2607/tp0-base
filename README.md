# Enunciado
### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).

# Solución
### Protocolo
Los mensajes son envíados con el siguiente formato:
`<msg id: ui8><longitud mensaje: uint32><longitud campo1: uint32><campo1: string>...`.

El cliente envía los datos de la apuesta al servidor con el msg id `STORE_BET` y espera a que este le responda para asegurar
que llegó la apuesta.

El servidor handlea el mensaje recibido y contesta con un mensaje `ok` enviado con el formato 
`<longitud mensaje: uint32><mensaje: str>`.

### Responsabilidades
Las responsabilidades fueron separadas en dos archivos (tanto para el cliente como para el servidor):
* `betting_protocol`: donde se encuentra que mensajes enviar, recibir y lógica como esperar a que el
  servidor conteste.
* `serializer`: se encuentran definidas acá las funciones que serializan y deserializan los datos.

Los archivos de server y client son los encargados de manejar la lógica de negocio.

### Manejo de short reads y short writes
Tanto en el servidor como en el cliente se crearon funciones del estilo `writeExactly` y `recvExactly`
que se aseguran de enviar o leer todos los bytes.

### Ejemplo de salida:
```
server   | 2025-03-24 03:13:53 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2025-03-24 03:13:53 INFO     action: accept_connections | result: in_progress
server   | 2025-03-24 03:13:53 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2025-03-24 03:13:53 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: STORE_BET
server   | 2025-03-24 03:13:53 INFO     action: apuesta_almacenada | result: success | dni: 30904465 | numero: 7574
server   | 2025-03-24 03:13:53 INFO     action: accept_connections | result: in_progress
client1  | 2025-03-24 03:13:53 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 500 | loop_period: 150ms | log_level: INFO
client1  | 2025-03-24 03:13:53 INFO     action: sending_bet | result: in_progress | bet_number: 7574
client1  | 2025-03-24 03:13:53 INFO     action: apuesta_enviada | result: success | dni: 30904465 | numero: 7574
```
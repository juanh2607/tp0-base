# Enunciado
### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

# Solución
Se setea la variable de entorno `CLIENTS` al crear el compose file usando `generar-compose.sh`.
Esto permite al servidor saber cuando comenzar el sorteo (se recibieron todas las apuestas de todas las agencias).

Para saber con que agencia se está comunicando, se creo el mensaje `SYN` que contiene el ID de la agencia.
El servidor guarda el socket en un diccionario `agency id : socket`, contesta `ok` y el cliente empieza el envío de batches.

Cuando el cliente termina con el envío de apuestas, envía un mensaje `END_BETS` y el servidor continúa con el siguiente cliente (si lo hay), dejando abierta la conexión con el cliente para cuando tenga que enviar el resultado del sorteo.

El cliente se queda a la espera de recibir el ganador.


Una vez que el servidor recibió todos los mensages `END_BET` que esperaba, comienza con el sorteo. Se evalúan todas las apuestas para encontrar las ganadoras.

Las apuestas ganadoras se guardan en un diccionario `agency id : winners` donde `winners` es un listado de documentos.

Al finalizar el conteo, se le envía a la agencia solo sus correspondientes ganadores, aprovechando los diccionarios.
Este mensaje se envía con el formato `<total_length: uint32><DNI1;DNI2;...: string>`.

El cliente recibe el listado de ganadores e imprime la cantidad como pide el enunciado, finalizando su ejecución.
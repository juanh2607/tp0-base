# Enunciado
### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

# Solución [WIP]

El servidor va a tener una variable de entorno con la cantidad de clientes.

Va a recibir las apuestas, de forma secuencial ya que solo procesa un cliente a la vez.

Cuando recibe un END_BETS, avanza con el siguiente. Si ya recibió todos los end_bets que esperaba,
realiza el sorteo.
El cliente se queda esperando.

Importante: diccionario con los sockets (agencia: socket)

Realiza el sorteo, es guardar un diccionario agency: [dni ganadores] y se lo mandas por socket.

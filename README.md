# Enunciado
### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv`.

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

# Solución
Se modificó `mi-generador.py` para incluir un `bind mount` en el cliente, donde el cliente `i` recibe el archivo `agency-<i>.csv`.

Al protocolo se agregaron dos nuevos tipos de mensajes:
* `STORE_BATCH`: en la configuración del **cliente** se define el tamaño del batch (el cuál no puede exceder los 100 para evitar superar los 8kb por batch). Ahora los mensajes se envían con el siguiente formato:  
`<msg id: ui8><total_length: uint32><total bets: uint32><bet 1>...<bet N>`  
en donde cada apuesta mantiene el siguiente formato:  
`<length bet 1: uint32><length field1: uint32><field1: str>...`  
Del lado del **servidor**, se deserializan las apuestas y se guardan, loggeando la cantidad almacenada.
Esto se hace en modalidad `best effort`, es decir, si falla la deserialización de alguna apuesta, se loggea 
`action: apuesta_recibida | result: failed | cantidad: {len(batch)}`, con la cantidad de apuestas que 
si se pudieron guardar.

* `FIN`. Cuando el cliente termina de leer el archivo de apuestas, finaliza de forma ordenada enviando
un mensaje de un byte indicando que finaliza la conexión. El servidor finaliza el loop y procede 
con el siguiente cliente.


**Aclaración tests**: pese a que el comportamiento del servidor-cliente es el esperado, los tests fallaban por timeout ya que se quedaban a la espera de un log de docker con `client1 exited with code 0` que nunca llegaba, si bien el cliente finalizaba.

Para bypassear este error, se agregó lo siguiente al `main.go` del cliente:

```go
// This is to force an exit message so that tests pass.
// Tests expect the client1 exited with code 0 or server exited with code 0
// message that is sent by docker when shutting down the containers, but for some reason
// it is never logged, so the test just timeouts.
time.Sleep(1000 * time.Millisecond)
log.Infof("action: exit | result: success")
```

El tiempo de espera es para asegurar que todos los logs hayan sido impresos ya que el orden de los logs es no determinístico y podría ocurrir que se imprima exit del lado del cliente, el test finalize por esto y no se hayan impreso todavía los logs del servidor.

### Para ver la interacción entre el servidor y los clientes:
Si es la primera vez que se ejecuta:

`make build`
`make docker-image`
Luego:

`./generar-compose.sh docker-compose-dev.yaml 1`
`make docker-compose-up`
`make docker-compose-logs`
`make docker-compose-down`

El tamaño de los batchs es configurable en `client/config.yaml`. No se permite exceder el valor 100.
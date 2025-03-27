# Enunciado
### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

# Solución
Debdio al `Global Interpreter Lock` de Python, los threads no pueden ejecutar bytecode en paralelo. Esto puede llegar a traer problemas de performance, pero dado que los threads en el servidor pasan la mayor parte del tiempo realizando operaciones I/O, no es un problema en este caso.

Igualmente, para poder procesar los mensajes en paralelo, es necesario usar el módulo [multiprocessing](https://docs.python.org/3/library/multiprocessing.html), el cuál permite evitar el `GIL`, usando procesos en lugar de threads.

Esto efectivamente permite el procesamiento en paralelo en Python.


Para evitar condiciones de carrera sobre recursos compartidos, se emplearon locks. En particular se emplearon los locks de `multiprocessing.Lock()`.  
Estos fueron utilizados para proteger las secciones críticas del programa, las cuales son:
* La escritura del archivo de apuestas al hacer `store_bets`
* La escritura de la variable `self._ended_clients` para determinar cuando comenzar con las apuestas.
* La lectura del archivo de apuestas al hacer `load_bets`
* La modificación del diccionario de victorias `self._winners`


Al finalizar, se limpian todos los recursos del servidor:  
```
server   | 2025-03-27 20:13:19 INFO     action: sorteo | result: success
server   | 2025-03-27 20:13:19 INFO     action: closing_socket | result: success | agency_id: 4
server   | 2025-03-27 20:13:19 INFO     action: closing_socket | result: success | agency_id: 5
server   | 2025-03-27 20:13:19 INFO     action: closing_socket | result: success | agency_id: 3
server   | 2025-03-27 20:13:19 INFO     action: closing_socket | result: success | agency_id: 2
server   | 2025-03-27 20:13:19 INFO     action: closing_socket | result: success | agency_id: 1

server   | 2025-03-27 20:13:39 INFO     action: shutdown | result: in_progress
server   | 2025-03-27 20:13:39 INFO     action: closing_listener | result: success
server   | 2025-03-27 20:13:39 INFO     action: terminating_process | pid: 39
server   | 2025-03-27 20:13:39 INFO     action: terminating_process | pid: 41
server   | 2025-03-27 20:13:39 INFO     action: terminating_process | pid: 44
server   | 2025-03-27 20:13:39 INFO     action: terminating_process | pid: 48
server   | 2025-03-27 20:13:39 INFO     action: terminating_process | pid: 54
server   | 2025-03-27 20:13:39 INFO     action: terminating_processes | result: success
server   | 2025-03-27 20:13:39 INFO     action: shutdown | result: success
server exited with code 0
```

En particular, a los procesos se los termina enviando una señal de terminación y se los espera con
`.join()`.


### Como ejecutar
Si es la primera vez que se ejecuta:

`make build`  
`make docker-image`  
Luego:  

`./generar-compose.sh docker-compose-dev.yaml 5`  
`make docker-compose-up`  
`make docker-compose-logs`  
`make docker-compose-down`  

**Obs**: si se ejecuta `make docker-compose-down` desde otra terminal, se puede observar el cierre ordenado del servidor.
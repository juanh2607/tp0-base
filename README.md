# Enunciado
### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

# Solución
Debdio al `GIL` de Python, los threads no pueden ejecutar el mismo bytecode en paralelo. Esto puede llegar a traer problemas de performance, pero dado que los threads en el servidor pasan la mayor parte del tiempo realizando operaciones I/O, no es un problema en este caso.
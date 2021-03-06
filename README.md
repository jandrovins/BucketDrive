# BucketDrive

Práctica 1 para la materia de Telemática ST0255.

### Integrantes:

- Vincent Alejandro Arcila Larrea

- Isabel Piedrahíta Vélez

## 1. Especificación del Servicio

El presente es un servicio de almacenamiento de archivos como documentos, imágenes, archivos binarios, entre otros donde cada archivo se considera un objeto y puede ser almacenado en un contenedor denominado bucket que se encuentra en un servidor. Esto se hizo con la intención de que cada usuario pueda acceder de forma remota a consultar alguno de los archivos en el servidor. Para lograr esto, se desarrolló un protocolo de capa de aplicación que permite a los usuarios acceder al servicio de forma consistente y realizar diferentes acciones listadas a continuación.

1. Crear un buket.

2. Eliminar un bucket.

3. Listar los buckets existentes en el directorio de trabajo.

4. Listar los archivos que hay en un bucket definido.

5. Eliminar un archivo en un bucket definido.

6. Realizar la carga de un archivo a un bucket definido.

7. Descargar un archivo del servidor al cliente.


Para efectos de facilidad de uso se desarrolló una shell interactiva llamada BucketShell para el cliente, en la que se implementaron además de los comandos básicos de BucketDrive comandos de ayuda para el usuario. Estos comandos de ayuda listan la sintaxis correcta de cada una de estas operaciones y explican lo que cada una hace. Las instrucciones para llamar a estas ayudas son visibles cuando el cliente accede a BucketShell.

Finalmente, algunas consideraciones adicionales sobre el servicio. El comportamiento del servidor se presta para manejar a multiples clientes de manera concurrente por medio de threads, cada cliente puede conectarse y desconectarse del servidor en el momento que lo considere. Del mismo modo, el cliente puede descargar y subir archivos al servidor sin perder conexión ni la capacidad de hacer otras peticiones al servidor. El servidor tiene la capacidad de recibir comandos del cliente aún si se encuentra enviando un archivo de respuesta a este. Tanto los buckets como los archivos dentro de los mismos tienen un identificador único que coincide con el nombre que el usuario les haya dado, por lo que bucket drive no tiene soporte para buckets o archivos de igual nombre que uno previamente existente. Por último, para garantizar la transparencia en operaciones, tanto el servidor como el cliente generan un log en donde sus actividades son visibles y fácilmente rastreables.

## 2. Vocabulario del Mensaje

BucketDrive utiliza una misma estructura de mensaje para todas sus comunicaciones; nuestros mensajes están divididos en 2: 

Un header de tamaño constante y un payload de tamaño variable. En el header se envía un entero con el tamaño del payload del mensaje, formateado en big-endian y en ‘unsigned long long’. De este modo, el receptor siempre sabe cuántos bytes leer del socket para procesar el payload.
El payload siempre está  formateado en JSON, y codificado en “UTF-8”. Con este formato de mensaje, simplificamos en gran medida el proceso de leer un mensaje, pues al ser un JSON el formato es constante e independiente del contexto. 

Cuando el mensaje lo envía el cliente: en el payload enviamos el tipo de instrucción que debe realizar el servidor, así como los parámetros necesarios para  este. Por ejemplo, en el campo “instruction_type” iría el tipo de instrucción 1 (en nuestro código los tipos de instrucción los manejamos con enumeraciones) con lo cual el servidor ya sabe que la instrucción a realizar es crear un bucket, y en el campo “bucket_name” del JSON iría una string con el nombre del bucket a crear.

Cuando el mensaje lo envía el servidor: este mensaje sería casi siempre de tipo respuesta, enviando la información pedida por el cliente. En el campo “response” del payload iría la cadena de texto de respuesta.

El cliente también envía mensajes de tipo respuesta, del mismo modo que lo acabamos de ilustrar para el servidor. Las conexiones siempre comparten el estado del proceso con su contraparte.

En BucketDrive existe un mensaje especial: aquel que lleva consigo un archivo. Para estos casos, luego de enviarse el payload, también se enviará el tamaño del archivo a enviar, del mismo modo que se envía el primer header. Seguidamente se enviará el archivo.

A continuación la estructura gráfica del mensaje:

![image.png](attachment:0ecd762e-bc41-4b73-a35c-6d490838097e.png)

## 3. Regla de Procedimientos

La estructura general del protocolo se explica en el siguiente diagrama.

![image.png](attachment:2dfc5f48-db82-44bf-82b0-33fdf5cf3035.png)

Los mensajes que puede enviar el cliente están definidos de la siguiente forma. En la tabla verá el valor real o sintáctico y entre paréntesis su significado semántico en la columna de Header, mientras que en la columna de Payload encontrará la estructura del JSON correspondiente, en la que es muy fácil deducir a que se refiere el código y por ende no se pondrá entre paréntesis su significado semántico. Todas estas peticiones de cliente son independientes entre si y el servidor no requiere mantener información de estado para manejar estas.

| Header | Payload   |
|------|------|
|   1 (CREATE_BUCKET) | "bucket_name": bucket_name |
|   2 (REMOVE_BUCKET)| "bucket_name": bucket_name |
|   3 (LIST_BUCKETS) | no_payload_info |
|   4 (REMOVE_FILE_FROM_BUCKET) | "bucket_name": bucket_name, "file_name": file_name |
|   5 (LIST_FILES_FROM_BUCKET) | "bucket_name": bucket_name |
|   6 (UPLOAD_FILE) | "bucket_name": bucket_name, "file_name": file_name |
|   7 (DOWNLOAD_FILE) | "bucket_name": bucket_name, "file_name": file_name |

Los mensajes recibidos son todos muy similares en estructura, contienen un output que representa la información que se le debe mostrar al cliente. Este output es una string. Siempre que se envía un mensaje, se debe esperar un mensaje de respuesta.

| Header | Payload   |
|------|------|
| len (longitud del contenido que se leerá) | "response": output (respuesta que debe ser mostrada al cliente) |

Los errores en BucketDrive se manejan mediante la captura de excepciones, hay principalmente tres tipos de error, error de conección, error en tipo de dato y error en existencia tanto de bucket cómo de archivo. Los errores de coneccion se manejan levantando una excepción de tipo RuntimeError("socket connection broken"), no retornan nada al cliente. Los mensajes de falla en tipo de dato se manejan capturando la excepción y retornando al usuario un mensaje de error que quiere decir que alguno de los valores ingresados no se encuentra en la forma correcta. Los errores de inexistencia se manejan muy similarmente a los anteriores, se captura la excepción y se retorna al usuario un mensaje que explica que no se encontró el bucket o archivo deseado. A continuación hay una tabla con cada error y los mensajes que imprime en la consola interactiva.

| Error | Mensaje   |
|------|------|
| Error de conección |  |
| Error de tipo | Assertions failed in 'remove_file_from_bucket': {e} |
| Error de inexistencia | ERROR: Bucket '{bucket_name}' does not exist inside root directory '{ROOT_PATH}', ERROR: file '{file}' does not exist inside bucket '{bucket_name}' |

El procesamiento de mensajes se da en la función read() para los mensajes que van del cliente al servidor. En esta función se decodifica el tipo de instrucción y los parámetros y con esta información se llama a la función requerida. El procesamiento de los mensajes que van del servidor al cliente se da en la función recv_message() en la que se extrae la respuesta del JSON que trae el mensaje y se imprime directamente a BucketShell.



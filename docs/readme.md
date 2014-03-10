## Como ejecutar en produccion

Para ejecutar en produccion es necesario tener instalado uwsgi (http://uwsgi-docs.readthedocs.org/) y ejecutar:

    NEW_RELIC_CONFIG_FILE=conf/newrelic.ini
    export NEW_RELIC_CONFIG_FILE

    newrelic-admin run-program uwsgi --ini conf/uwsgi.ini

Atencion a que uwsgi hace chroot del directorio base de la aplicacion, es por eso que es necesario incluir el directorio conf/ en la varialbe de entorno `NEW_RELIC_CONFIG_FILE`.

Adicionalmente a esto es necesario un nginx (cuya configuración también se encuentra en el directorio conf) que envíe solicitudes mediante uwsgi a un socket.

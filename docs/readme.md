## Como ejecutar en produccion

Para ejecutar en produccion es necesario tener instalado uwsgi (http://uwsgi-docs.readthedocs.org/) y ejecutar:

    NEW_RELIC_CONFIG_FILE=newrelic.ini
    export NEW_RELIC_CONFIG_FILE

    newrelic-admin run-program uwsgi --conf conf/uwsgi.ini

Adicionalmente a esto es necesario un nginx (cuya configuración también se encuentra en el directorio conf) que envíe solicitudes mediante uwsgi a un socket.

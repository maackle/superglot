ROOT=/home/superglot/server
export NEW_RELIC_CONFIG_FILE=$ROOT/conf/newrelic.ini
export SUPERGLOT_SETTINGS="superglot.config.envs.staging"
/home/superglot/.virtualenvs/superglot/bin/newrelic-admin run-program /home/superglot/.virtualenvs/superglot/bin/gunicorn -w 4 -b 127.0.0.1:6107 -t 240 --pythonpath $ROOT wsgi:app

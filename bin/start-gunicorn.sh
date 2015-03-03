
NEW_RELIC_CONFIG_FILE=conf/newrelic.ini
SUPERGLOT_SETTINGS=superglot/config/envs/production.py
/home/superglot/.virtualenvs/superglot/bin/newrelic-admin run-program /home/superglot/.virtualenvs/superglot/bin/gunicorn -w 4 -b 127.0.0.1:6107 -t 240 --pythonpath /home/superglot/server superglot:app

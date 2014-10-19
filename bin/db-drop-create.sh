psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$1'"
psql -c "DROP DATABASE $1;"
psql -c "CREATE DATABASE $1;"
psql -c "GRANT ALL ON DATABASE superglot_dev TO $1;"
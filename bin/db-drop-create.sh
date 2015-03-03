psql -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$1'"
psql -d postgres -c "DROP DATABASE $1;"
psql -d postgres -c "CREATE DATABASE $1;"
psql -d postgres -c "GRANT ALL ON DATABASE $1 TO $1;"

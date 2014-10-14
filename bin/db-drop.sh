psql -c "DROP DATABASE superglot_dev;"
psql -c "CREATE DATABASE superglot_dev;"
psql -c "GRANT ALL ON DATABASE superglot_dev TO superglot_dev;"
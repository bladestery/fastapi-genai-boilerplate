# Calculating Embeddings

run using python notebook

Chunk based on page. Pages could be truncated when calculating embeddings but unlikely.


# Importing embeddings.csv into database

docker cp /path/to/local/data.csv <container_id_or_name>:/tmp/data.csv

docker exec -it <container_id_or_name> psql -U <username> -d <database_name>

COPY <table_name> FROM '/tmp/data.csv' DELIMITER ',' CSV;


    CREATE EXTENSION vector;
    CREATE TABLE my_items (id INT PRIMARY KEY,description TEXT,embedding VECTOR(3072));
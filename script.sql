- créer un user (role) et une base
CREATE USER tp_user WITH PASSWORD 'tp_password';
CREATE DATABASE tp_db OWNER tp_user;
GRANT ALL PRIVILEGES ON DATABASE tp_db TO tp_user;
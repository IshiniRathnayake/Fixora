-- Run once as MySQL root (before schema.sql) when NOT using Docker.
-- Creates the app user expected by .env.example

CREATE USER IF NOT EXISTS 'fixora'@'localhost' IDENTIFIED BY 'fixora_dev_password';
CREATE USER IF NOT EXISTS 'fixora'@'%' IDENTIFIED BY 'fixora_dev_password';

GRANT ALL PRIVILEGES ON fixora.* TO 'fixora'@'localhost';
GRANT ALL PRIVILEGES ON fixora.* TO 'fixora'@'%';

FLUSH PRIVILEGES;

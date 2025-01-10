USE detectors_db;
CREATE TABLE detectors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL UNIQUE,
    `key` VARCHAR(255) NOT NULL
);

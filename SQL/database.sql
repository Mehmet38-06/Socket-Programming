USE communication_logs;

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    protocol VARCHAR(10),
    receiver_ip VARCHAR(45),
    sender_ip VARCHAR(45),
    direction VARCHAR(10),
    status TINYINT(1),  -- BOOLEAN yerine TINYINT(1) kullanılıyor
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


SELECT * FROM messages WHERE protocol = 'TCP'; 


USE communication_logs;

CREATE TABLE IF NOT EXISTS server_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_ip VARCHAR(45),
    server_port INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


SELECT * FROM server_logs;




GRANT ALL PRIVILEGES ON *.* TO 'your_sql_server_name'@'client_IP' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;


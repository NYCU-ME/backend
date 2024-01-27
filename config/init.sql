USE `nycu_me_dns`;

CREATE USER IF NOT EXISTS 'nycu_dns'@'%' IDENTIFIED BY 'abc123';
GRANT ALL PRIVILEGES ON `nycu_me_dns`.* TO 'nycu_dns'@'%';
FLUSH PRIVILEGES;

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
      `id` varchar(256) NOT NULL,
      `name` varchar(256) NOT NULL,
      `username` varchar(256) NOT NULL,
      `password` varchar(100) NOT NULL DEFAULT '',
      `status` varchar(16) NOT NULL,
      `email` varchar(256) NOT NULL,
      `limit` int(11) NOT NULL DEFAULT '5',
      `isAdmin` int(11) NOT NULL DEFAULT '0',
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `domains`
--

CREATE TABLE `domains` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `userId` varchar(256) NOT NULL,
      `domain` text,
      `regDate` datetime DEFAULT NULL,
      `expDate` datetime DEFAULT NULL,
      `status` tinyint(1) DEFAULT '1',
      PRIMARY KEY (`id`),
      KEY `userId_idx` (`userId`),
      CONSTRAINT `domains_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4;


DELIMITER $$

CREATE TRIGGER before_insert_domains
BEFORE INSERT ON domains FOR EACH ROW
BEGIN
    IF NEW.status = 1 AND (
        SELECT COUNT(*)
        FROM domains
        WHERE domain = NEW.domain AND status = 1
    ) > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This domain has been registered';
    END IF;
END$$

DELIMITER ;

--
-- Table structure for table `records`
--

CREATE TABLE `records` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `domain` int(11) NOT NULL,
      `type` char(16) NOT NULL,
      `value` varchar(256) DEFAULT NULL,
      `ttl` int(11) NOT NULL,
      `regDate` datetime DEFAULT NULL,
      `expDate` datetime DEFAULT NULL,
      `status` tinyint(1) DEFAULT '1',
      KEY `domain_idx` (`domain`),
      PRIMARY KEY (`id`),
      CONSTRAINT `records_ibfk_1` FOREIGN KEY (`domain`) REFERENCES `domains` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `glues` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `domain` int(11) NOT NULL,
      `subdomain` text,
      `type` char(16) NOT NULL,
      `ttl` int(11) NOT NULL,
      `value` varchar(256) DEFAULT NULL,
      `regDate` datetime DEFAULT NULL,
      `expDate` datetime DEFAULT NULL,
      `status` tinyint(1) DEFAULT '1',
      KEY `domain_idx` (`domain`),
      PRIMARY KEY (`id`),
      CONSTRAINT `glues_ibfk_1` FOREIGN KEY (`domain`) REFERENCES `domains` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `dnskeys` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `domain` int(11) NOT NULL,
      `ttl` int(11) NOT NULL,
      `flag` int(11) NOT NULL,
      `algorithm` int(11) NOT NULL,
      `value` varchar(512) DEFAULT NULL,
      `regDate` datetime DEFAULT NULL,
      `expDate` datetime DEFAULT NULL,
      `status` tinyint(1) DEFAULT '1',
      KEY `domain_idx` (`domain`),
      PRIMARY KEY (`id`),
      CONSTRAINT `dnskey_ibfk_1` FOREIGN KEY (`domain`) REFERENCES `domains` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


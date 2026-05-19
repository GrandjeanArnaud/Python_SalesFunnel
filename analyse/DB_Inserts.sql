INSERT INTO sectors (id, code, label) VALUES
(1, 'hair_salon', 'Hair Salon'),
(2, 'beauty_salon', 'Beauty Salon'),
(3, 'barber', 'Barber'),
(4, 'spa', 'Spa');

INSERT INTO contacts (id, name, last_name, first_name, email, interests, sector_id ) 
VALUES
( 1, 'Salon Élégance', 'Dupont', 'Alex', 'alex@salon.be', '{}', 1),
( 2, 'Beauty Glow', 'Martin', 'Sophie', 'sophie@beauty.be', '{}', 2),
( 3, 'Barber House', 'Bernard', 'Luc', 'luc@barber.be', '{}', 3),
( 4, 'Zen Spa Center', 'Leroy', 'Emma', 'emma@spa.be', '{}', 4),
( 5, 'Modern Cut Studio', 'Durand', 'Tom', 'tom@salon.be', '{}', 1),
( 6, 'Pure Beauty Lounge', 'Moreau', 'Nina', 'nina@beauty.be', '{}', 2),
( 7, 'Prestige Coiffure', 'Lambert', 'Pierre', 'pierre@salon.be', '{}', 1),
( 8, 'Relax Spa Retreat', 'Robert', 'Lea', 'lea@spa.be', '{}', 4), 
( 9, 'Classic Barber Club', 'Girard', 'Mike', 'mike@barber.be', '{}', 3),
( 10, 'Beauty Harmony', 'Fournier', 'Anna', 'anna@beauty.be', '{}', 2);


INSERT INTO interests (id, name, parent) VALUES

-- HAIR SALON & BARBER
(1,'hair_care',NULL),
(2,'shampoo','1'),
(3,'conditioner','1'),
(4,'treatment','1'),

(5,'dry_hair','2'),
(6,'oily_hair','2'),
(7,'colored_hair','2'),
(8,'damaged_hair','2'),
(9,'anti_dandruff','2'),

(10,'hair_styling',NULL),
(11,'gel','10'),
(12,'wax','10'),
(13,'spray','10'),

-- SPA
(20,'spa_care',NULL),
(21,'exfoliation','20'),
(22,'body_scrub','21'),
(23,'facial_scrub','21'),

(24,'relaxation_treatment','20'),
(25,'massage_products','20'),

(26,'bath_products','20'),
(27,'bath_salts','26'),
(28,'essential_oils','26'),

-- BEAUTY SALON
(30,'makeup',NULL),
(31,'foundation','30'),
(32,'concealer','30'),
(33,'lipstick','30'),
(34,'mascara','30'),

(35,'skincare_beauty',NULL),
(36,'face_cream','35'),
(37,'anti_aging','35'),
(38,'moisturizer','35'),

(39,'beauty_tools',NULL),
(40,'brushes','39'),
(41,'beauty_devices','39');


INSERT INTO interest_sectors (interest_id, sector_id) VALUES

-- Hair salon
(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),
-- Barber
(1,3),(2,3),(5,3),(6,3),(8,3),(10,3),(11,3),(12,3),(13,3),
-- Spa
(20,4),(21,4),(22,4),(23,4),(24,4),(25,4),(26,4),(27,4),(28,4),
-- Beauty salon
(30,2),(31,2),(32,2),(33,2),(34,2),(35,2),(36,2),(37,2),(38,2),(39,2),(40,2),(41,2);

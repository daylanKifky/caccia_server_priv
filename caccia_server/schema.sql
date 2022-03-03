

DROP TABLE IF EXISTS cards;
CREATE TABLE cards(
    id INTEGER PRIMARY KEY,
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image TEXT NOT NULL,
    enigmatype VARCHAR(30), -- question, radiobutton, physical
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    mapimage TEXT NOT NULL
);

INSERT INTO `cards` VALUES (0, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (1, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (2, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg"  );
INSERT INTO `cards` VALUES (3, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (4, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (5, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (6, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (7, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (8, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );
INSERT INTO `cards` VALUES (9, CURRENT_TIMESTAMP, "https://via.placeholder.com/150", 'question', "do you like puppies?",  'yes', "/static/map_not_found.jpg" );


DROP TABLE IF EXISTS users;
CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lastseen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    firstanswer TIMESTAMP,
    playtime INTEGER DEFAULT 0,
    enigma0 INTEGER DEFAULT 0,
    enigma1 INTEGER DEFAULT 0,
    enigma2 INTEGER DEFAULT 0,
    enigma3 INTEGER DEFAULT 0,
    enigma4 INTEGER DEFAULT 0,
    enigma5 INTEGER DEFAULT 0,
    enigma6 INTEGER DEFAULT 0,
    enigma7 INTEGER DEFAULT 0,
    enigma8 INTEGER DEFAULT 0,
    enigma9 INTEGER DEFAULT 0

);


DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Serv;
DROP TABLE IF EXISTS Frequency;
DROP TABLE IF EXISTS LoginStatus;
DROP TABLE IF EXISTS UserType;
DROP TABLE IF EXISTS HistoryRecored;

CREATE TABLE User(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    pwd TEXT NOT NULL,
    info TEXT,
    lable TEXT
);

CREATE TABLE Serv(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servname TEXT UNIQUE NOT NULL,
    servtype TEXT NOT NULL,
    servinfo TEXT,
    serventrance TEXT
);

CREATE TABLE UserType(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL,
    typeid INTEGER NOT NULL
);

CREATE TABLE LoginStatus(
    token TEXT PRIMARY KEY,
    userId INTEGER UNIQUE NOT NULL,
    loginTime DATETIME
);

CREATE TABLE HistoryRecored(
    recordId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    recordType INTEGER NOT NULL ,
    recordName varchar(255) NOT NULL,
    visitedUrl varchar(255),
    visitedTime DATETIME
);
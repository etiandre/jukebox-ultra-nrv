CREATE TABLE "users" (
    "user" TEXT NOT NULL PRIMARY KEY,
    "pass" TEXT
);
;
CREATE TABLE "macs" (
    "user" TEXT NOT NULL,
    "mac" TEXT NOT NULL PRIMARY KEY
);
;
CREATE TABLE "track_info" (
    "url" TEXT NOT NULL,
    "track" TEXT,
    "artist" TEXT,
    "album" TEXT,
    "duration" TEXT,
    "albumart_url" TEXT
);
CREATE TABLE log (
    "id" INTEGER,
    "url" TEXT NOT NULL
, "time" INTEGER, "mac" TEXT);
CREATE TABLE "likes" (
    "url" TEXT,
    "mac" TEXT,
    "value" TEXT
);

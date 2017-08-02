CREATE TABLE "users" (
    "user" TEXT NOT NULL PRIMARY KEY,
    "pass" TEXT
);
;
CREATE TABLE "macs" (
    "user" TEXT NOT NULL,
    "mac" TEXT NOT NULL PRIMARY KEY
);
CREATE TABLE log (
    "id" INTEGER,
    "url" TEXT NOT NULL,
    "album" TEXT,
    "artist" TEXT,
    "albumart_url" TEXT,
    "track" TEXT,
    "duration" INT
);

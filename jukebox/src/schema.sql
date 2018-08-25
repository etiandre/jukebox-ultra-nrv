CREATE TABLE "users" (
    "user" TEXT NOT NULL PRIMARY KEY,
    "pass" TEXT
);
CREATE TABLE "track_info" (
    "url" TEXT NOT NULL,
    "track" TEXT,
    "artist" TEXT,
    "album" TEXT,
    "duration" TEXT,
    "albumart_url" TEXT
);
CREATE TABLE log (
    "id" INTEGER PRIMARY KEY,
    "track" TEXT NOT NULL,
	"time" INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"user" TEXT NOT NULL
);

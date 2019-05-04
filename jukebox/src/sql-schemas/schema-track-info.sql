CREATE TABLE IF NOT EXISTS "track_info" (
    "id"        INTEGER PRIMARY KEY,
    "url"       TEXT NOT NULL,
    "track"     TEXT,
    "artist"    TEXT,
    "album"     TEXT,
    "duration"  INT,
    "albumart_url" TEXT,
    "source"    TEXT,
    "blacklisted" BOOLEAN DEFAULT 0
);

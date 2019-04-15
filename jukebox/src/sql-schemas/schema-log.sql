CREATE TABLE log (
    "id" INTEGER PRIMARY KEY,
    "track" INT references track_info(id),
    "time" INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user" INT references users(id)  
);

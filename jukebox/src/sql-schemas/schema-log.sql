CREATE TABLE log (
    "id" INTEGER PRIMARY KEY,
    trackid INTEGER,
    userid INTEGER,
    "time" INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(trackid) references track_info(id),
    FOREIGN KEY(userid) references users(id)  
);

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

DROP TABLE IF EXISTS sq03_clues;
DROP TABLE IF EXISTS sq03_verification;

CREATE TABLE "sq03_clues" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "sponsor_pk" VARCHAR(100),
  "sponsor_sk" VARCHAR(100),
  "claimant_pk" VARCHAR(100),
  "claimant_sk" VARCHAR(100),
  "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
)
;

CREATE TABLE "sq03_verification" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "sponsor" VARCHAR(100),
  "claimant" VARCHAR(100),
  "success" INTEGER,
  "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
)
;

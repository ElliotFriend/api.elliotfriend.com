DROP TABLE IF EXISTS sq03_clues;

CREATE TABLE "sq03_clues" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "sponsor_pk" VARCHAR(100),
  "sponsor_sk" VARCHAR(100),
  "claimant_pk" VARCHAR(100),
  "claimant_sk" VARCHAR(100),
  "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
)
;

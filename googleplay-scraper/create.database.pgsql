CREATE TABLE apkinformation
(
  id SERIAL PRIMARY KEY NOT NULL,
  name VARCHAR,
  apkname VARCHAR,
  version VARCHAR,
  developer VARCHAR NOT NULL,
  genre VARCHAR,
  userrating VARCHAR,
  numberofreviews INT,
  datepublished VARCHAR NOT NULL,
  filesize VARCHAR,
  numberofdownloads VARCHAR,
  operatingsystems VARCHAR,
  url VARCHAR,
  sourceid INT,
  apkid VARCHAR,
  collectiondate VARCHAR,
  lowerdownloads INT,
  upperdownloads INT,
  generatedfilesize INT,
  modifieddatepublished VARCHAR,
  modifiedos INT,
  generatedversion INT,
  isdownloaded BOOL DEFAULT false,
  isreviewsdownloaded BOOL DEFAULT false,
  isjavaanalyze BOOL DEFAULT false,
  modifiedostext VARCHAR
);

CREATE TABLE reviews
(
  id SERIAL PRIMARY KEY NOT NULL,
  app_id VARCHAR NOT NULL,
  title VARCHAR NOT NULL,
  body VARCHAR NOT NULL,
  date TIMESTAMP NOT NULL
);
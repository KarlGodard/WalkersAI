PRAGMA foreign_keys = ON;


CREATE TABLE artists(
  constituentID INTEGER NOT NULL PRIMARY KEY,
  displayName VARCHAR(30),
  artistBio VARCHAR(40),
  nationality VARCHAR(30),
  gender VARCHAR(10),
  beginDate INTEGER,
  endDate INTEGER,
  wikiQID VARCHAR(10),
  ULAN INTEGER
);

CREATE TABLE artworks(
  title VARCHAR(60) NOT NULL,
  constituentID INTEGER NOT NULL,
  date VARCHAR(20),
  medium VARCHAR(40),
  dimensions VARCHAR(40),
  creditLine VARCHAR(60),
  accessionNumber INTEGER,
  classification VARCHAR(30),
  department VARCHAR(40),
  dateAcquired TIMESTAMP,
  cataloged VARCHAR(2),
  objectID INTEGER NOT NULL PRIMARY KEY,
  url VARCHAR(60),
  ThumbnailURL VARCHAR(60),
  circumference INTEGER,
  depth INTEGER,
  diameter INTEGER,
  height INTEGER,
  length INTEGER,
  weight INTEGER,
  width INTEGER,
  seatHeight INTEGER,
  duration INTEGER,
  Foreign Key(constituentID) References Artists(constituentID)
);
-- Title,
-- ConstituentID, - ID number of the artist in the artists table
-- Date, -- This will be a string for now as some dates are written: 1977-1978
-- Medium,
-- Dimensions,
-- CreditLine,
-- AccessionNumber,
-- Classification,
-- Department,
-- DateAcquired,
-- Cataloged,
-- ObjectID, - Actual ID/row number of the artwork
-- URL,
-- ThumbnailURL,
-- Circumference (cm),
-- Depth (cm),
-- Diameter (cm),
-- Height (cm),
-- Length (cm),
-- Weight (kg),
-- Width (cm),
-- Seat Height (cm),
-- Duration (sec.)


-- ConstituentID,
-- DisplayName,
-- ArtistBio, - This is just their nationality and year of birth/sometimes death
-- Nationality,
-- Gender,
-- BeginDate, - Unsure, but it looks like a 0 here means undefined/uncertain
-- EndDate, - Same as above
-- Wiki QID,
-- ULAN - Getty ID
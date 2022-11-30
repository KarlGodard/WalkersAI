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
  artist VARCHAR(60),
  constituentID INTEGER NOT NULL,
  artistBio VARCHAR(40),
  nationality VARCHAR(30),
  beginDate VARCHAR(6),
  endDate VARCHAR(6),
  gender VARCHAR(10),
  date VARCHAR(20),
  medium VARCHAR(40),
  dimensions VARCHAR(40),
  creditLine VARCHAR(60),
  accessionNumber INTEGER,
  classification VARCHAR(30),
  department VARCHAR(40),
  dateAcquired VARCHAR(20),
  cataloged VARCHAR(2),
  objectID INTEGER NOT NULL PRIMARY KEY,
  url VARCHAR(60),
  ThumbnailURL VARCHAR(60),
  circumference REAL,
  depth REAL,
  diameter REAL,
  height REAL,
  length REAL,
  weight REAL,
  width REAL,
  seatHeight REAL,
  duration REAL,
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
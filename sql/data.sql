PRAGMA foreign_keys = ON;
-- artistBio VARCHAR(40),
-- nationality VARCHAR(30),
-- gender VARCHAR(10),
-- beginDate INTEGER,
-- endDate INTEGER,

INSERT INTO artists(constituentID, displayName, nationality, gender, beginDate, endDate)
VALUES(1, "Leonardo da Vinci", "Italian", "Male", "1482", "1500");
--"Date": "1938",
--   "Medium": "Tempera on wood",
--    "Dimensions": "21 1/8 x 18 1/8\" (53.7 x 46 cm)",
--    "CreditLine": "Inter-American Fund",
--    "AccessionNumber": "702.1942",
--    "Classification": "Painting",
--    "Department": "Painting & Sculpture",
--    "DateAcquired": "1942-12-29",
INSERT INTO artworks(title, constituentID, objectID, date, medium, dimensions, dateAcquired)
VAlUES("Mona Lisa", 1, 1, "1503", "oil paints on a poplar wood panel", "2ft 6in x 1ft 9in", "1804");



-- INSERT INTO users(username, fullname, email, filename, password)
-- VALUES('awdeorio', 'Andrew DeOrio','awdeorio@umich.edu', 'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg',
-- 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');
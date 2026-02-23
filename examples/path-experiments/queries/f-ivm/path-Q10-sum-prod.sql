IMPORT DTREE FROM FILE 'path-Q10.txt';

CREATE STREAM R1 (
	A1 	 INT, 
	A2 	 INT) 
FROM FILE './datasets/snap/R1.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R2 (
	A2 	 INT, 
	A3 	 INT) 
FROM FILE './datasets/snap/R2.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R3 (
	A3 	 INT, 
	A4 	 INT) 
FROM FILE './datasets/snap/R3.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R4 (
	A4 	 INT, 
	A5 	 INT) 
FROM FILE './datasets/snap/R4.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R5 (
	A5 	 INT, 
	A6 	 INT) 
FROM FILE './datasets/snap/R5.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R6 (
	A6 	 INT, 
	A7 	 INT) 
FROM FILE './datasets/snap/R6.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R7 (
	A7 	 INT, 
	A8 	 INT) 
FROM FILE './datasets/snap/R7.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R8 (
	A8 	 INT, 
	A9 	 INT) 
FROM FILE './datasets/snap/R8.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R9 (
	A9 	 INT, 
	A10 	 INT) 
FROM FILE './datasets/snap/R9.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM R10 (
	A10 	 INT, 
	A11 	 INT) 
FROM FILE './datasets/snap/R10.csv' 
LINE DELIMITED CSV (delimiter := '|');


SELECT A1, A11, SUM(1)
FROM R1 NATURAL JOIN R2 NATURAL JOIN R3 NATURAL JOIN R4 NATURAL JOIN R5 NATURAL JOIN R6 NATURAL JOIN R7 NATURAL JOIN R8 NATURAL JOIN R9 NATURAL JOIN R10
GROUP BY A1, A11;



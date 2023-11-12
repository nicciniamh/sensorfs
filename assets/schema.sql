CREATE TABLE temphist_pi3(
	'temp' NUMBER NOT NULL,
	'humidity' NUMBER NOT NULL,
	'pressure' default 0,
	'time' NUMBER NOT NULL PRIMARY KEY,
	'hour' NUMBER NOT NULL
);
CREATE TABLE temphist_piz(
	'temp' NUMBER NOT NULL,
	'humidity' NUMBER NOT NULL,
	'pressure' default 0,
	'time' NUMBER NOT NULL PRIMARY KEY,
	'hour' NUMBER NOT NULL
);
CREATE TABLE temphist_pi4(
	'temp' NUMBER NOT NULL,
	'humidity' NUMBER NOT NULL,
	'pressure' NUMBER NOT NULL,
	'time' NUMBER NOT NULL PRIMARY KEY,
	'hour' NUMBER NOT NULL
);
CREATE TABLE thColNames (one string, two string, three string, four string);
CREATE VIEW tempHist as
SELECT datetime(a.time,'unixepoch','localtime') AS Date, a.temp AS Nicci, b.temp AS Terry, c.temp AS Living
FROM temphist_pi4 AS a
LEFT JOIN temphist_pi3 AS b ON a.time = b.time 
LEFT JOIN temphist_piz AS c ON a.time = c.time where a.temp is not null and b.temp is not null and c.temp is not null

CREATE VIEW tempHist2 as
SELECT a.time  AS time, a.temp AS Nicci, b.temp AS Terry, c.temp AS Living
FROM temphist_pi4 AS a
LEFT JOIN temphist_pi3 AS b ON a.time = b.time
LEFT JOIN temphist_piz AS c ON a.time = c.time where a.temp is not null and b.temp is not null and c.temp is not null
/* tempHist(Date,Nicci,Terry,Living) */
/* tempHist2(time,Nicci,Terry,Living) */

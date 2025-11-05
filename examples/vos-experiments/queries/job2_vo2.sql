IMPORT DTREE FROM FILE 'job2_vo2.txt';

CREATE STREAM TITLE (
	movie_id 	 INT, 
	t_title 	 VARCHAR(100), 
	t_imdb_index 	 VARCHAR(12), 
	kind_id 	 INT, 
	t_production_year 	 INT, 
	imdb_id 	 INT, 
	t_phonetic_code 	 VARCHAR(5), 
	t_episode_of_id 	 INT, 
	t_season_nr 	 INT, 
	t_episode_nr 	 INT, 
	t_series_years 	 VARCHAR(49), 
	t_md5sum 	 VARCHAR(32)) 
FROM FILE './datasets/imdb/TITLE.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM CAST_INFO (
	ci_id 	 INT, 
	person_id 	 INT, 
	movie_id 	 INT, 
	person_role_id 	 INT, 
	ci_note 	 VARCHAR(100), 
	ci_nr_order 	 VARCHAR(10),
	role_id 	 INT) 
FROM FILE './datasets/imdb/CAST_INFO.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM NAME (
	person_id 	 INT, 
	name 	 VARCHAR(100), 
	n_imdb_index 	 VARCHAR(12), 
	n_imdb_id 	 VARCHAR(12),
	n_gender 	 VARCHAR(1), 
	n_name_pcode_cf 	 VARCHAR(5), 
	n_name_pcode_nf 	 VARCHAR(5), 
	n_surname_pcode 	 VARCHAR(5), 
	n_md5sum 	 VARCHAR(32)) 
FROM FILE './datasets/imdb/NAME.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM MOVIE_KEYWORD (
	mk_id 	 INT, 
	movie_id 	 INT, 
	keyword_id 	 INT) 
FROM FILE './datasets/imdb/MOVIE_KEYWORD.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE STREAM KEYWORD (
	keyword_id 	 INT, 
	keyword 	 VARCHAR(100), 
	k_phonetic_code 	 VARCHAR(5)) 
FROM FILE './datasets/imdb/KEYWORD.csv' 
LINE DELIMITED CSV (delimiter := '|');


SELECT SUM(1) 
FROM TITLE NATURAL JOIN CAST_INFO NATURAL JOIN NAME NATURAL JOIN MOVIE_KEYWORD NATURAL JOIN KEYWORD;



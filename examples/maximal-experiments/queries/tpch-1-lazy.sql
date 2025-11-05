IMPORT DTREE FROM FILE '1.txt';

CREATE TABLE ORDERS (
	orderkey 	 int, 
	custkey 	 int, 
	o_orderstatus 	 char, 
	o_totalprice 	 double, 
	o_orderdate 	 string, 
	o_orderpriority 	 string, 
	o_clerk 	 string, 
	o_shippriority 	 int, 
	o_comment 	 string) 
FROM FILE './datasets/imdb/ORDERS.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE LINEITEM (
	orderkey 	 int, 
	partkey 	 int, 
	suppkey 	 int, 
	l_linenumber 	 int, 
	l_quantity 	 double, 
	l_extendedprice 	 double, 
	l_discount 	 double, 
	l_tax 	 double, 
	l_returnflag 	 char, 
	l_linestatus 	 char, 
	l_shipdate 	 string, 
	l_commitdate 	 string, 
	l_receiptdate 	 string, 
	l_shipinstruct 	 string, 
	l_shipmode 	 string, 
	l_comment 	 string) 
FROM FILE './datasets/imdb/LINEITEM.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE PARTSUPP (
	partkey 	 int, 
	suppkey 	 int, 
	ps_availqty 	 int, 
	ps_supplycost 	 double, 
	ps_comment 	 string) 
FROM FILE './datasets/imdb/PARTSUPP.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE PART (
	partkey 	 int, 
	p_name 	 string, 
	p_mfgr 	 string, 
	p_brand 	 string, 
	p_type 	 string, 
	p_size 	 int, 
	p_container 	 string, 
	p_retailprice 	 double, 
	p_comment 	 string) 
FROM FILE './datasets/imdb/PART.csv' 
LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE SUPPLIER (
	suppkey 	 int, 
	s_name 	 string, 
	s_address 	 string, 
	s_nationkey 	 int, 
	s_phone 	 string, 
	s_acctbal 	 double, 
	s_comment 	 string) 
FROM FILE './datasets/imdb/SUPPLIER.csv' 
LINE DELIMITED CSV (delimiter := '|');


SELECT SUM(1)
FROM ORDERS NATURAL JOIN LINEITEM NATURAL JOIN PARTSUPP NATURAL JOIN PART NATURAL JOIN SUPPLIER;


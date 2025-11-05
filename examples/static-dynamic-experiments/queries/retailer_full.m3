---------------- TYPE DEFINITIONS ---------------


-------------------- SOURCES --------------------
CREATE STREAM INVENTORY (locn int, dateid int, ksn int, inventoryunits int)
  FROM FILE './datasets/retailer/Inventory.tbl' LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE LOCATION (locn int, zip int, rgn_cd int, clim_zn_nbr int, tot_area_sq_ft int, sell_area_sq_ft int, avghhi int, supertargetdistance double, supertargetdrivetime double, targetdistance double, targetdrivetime double, walmartdistance double, walmartdrivetime double, walmartsupercenterdistance double, walmartsupercenterdrivetime double)
  FROM FILE './datasets/retailer/Location.tbl' LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE CENSUS (zip int, population int, white int, asian int, pacific int, blackafrican int, medianage double, occupiedhouseunits int, houseunits int, families int, households int, husbwife int, males int, females int, householdschildren int, hispanic int)
  FROM FILE './datasets/retailer/Census.tbl' LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE ITEM (ksn int, subcategory byte, category byte, categoryCluster byte, prize double)
  FROM FILE './datasets/retailer/Item.tbl' LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE WEATHER (locn int, dateid int, rain byte, snow byte, maxtemp int, mintemp int, meanwind double, thunder byte)
  FROM FILE './datasets/retailer/Weather.tbl' LINE DELIMITED CSV (delimiter := '|');

--------------------- MAPS ----------------------
DECLARE MAP V_locn_IIWLC1(long)[][] :=
  AggSum([],
    (V_dateid_IIW1(long)[][locn]<Local> * V_zip_LC1(long)[][locn]<Local>)
  );

DECLARE MAP V_dateid_IIW1(long)[][locn: int] :=
  AggSum([locn],
    (V_ksn_II1(long)[][locn, dateid]<Local> * V_rain_W1(long)[][locn, dateid]<Local>)
  );

DECLARE MAP V_ksn_II1(long)[][locn: int, dateid: int] :=
  AggSum([locn, dateid],
    (V_inventoryunits_I1(long)[][locn, dateid, ksn]<Local> * V_subcategory_I1(long)[][ksn]<Local>)
  );

DECLARE MAP V_inventoryunits_I1(long)[][locn: int, dateid: int, ksn: int] :=
  AggSum([locn, dateid, ksn],
    ((INVENTORY(locn, dateid, ksn, inventoryunits) ) )
  );

DECLARE MAP V_subcategory_I1(long)[][ksn: int] :=
  AggSum([ksn],
    ITEM(ksn, subcategory, category, categoryCluster, prize)
  );

DECLARE MAP V_rain_W1(long)[][locn: int, dateid: int] :=
  AggSum([locn, dateid],
    WEATHER(locn, dateid, rain, snow, maxtemp, mintemp, meanwind, thunder)
  );

DECLARE MAP V_zip_LC1(long)[][locn: int] :=
  AggSum([locn],
    (V_rgn_cd_L1(long)[][locn, zip]<Local> * V_population_C1(long)[][zip]<Local>)
  );

DECLARE MAP V_rgn_cd_L1(long)[][locn: int, zip: int] :=
  AggSum([locn, zip],
    LOCATION(locn, zip, rgn_cd, clim_zn_nbr, tot_area_sq_ft, sell_area_sq_ft, avghhi, supertargetdistance, supertargetdrivetime, targetdistance, targetdrivetime, walmartdistance, walmartdrivetime, walmartsupercenterdistance, walmartsupercenterdrivetime)
  );

DECLARE MAP V_population_C1(long)[][zip: int] :=
  AggSum([zip],
    CENSUS(zip, population, white, asian, pacific, blackafrican, medianage, occupiedhouseunits, houseunits, families, households, husbwife, males, females, householdschildren, hispanic)
  );

DECLARE MAP TMP_SUM1(long)[][locn: int, dateid: int, ksn: int] :=
  AggSum([locn, dateid, ksn],
    (((DELTA INVENTORY)(locn, dateid, ksn, inventoryunits) ) )
  );

DECLARE MAP TMP_SUM2(long)[][locn: int, dateid: int] :=
  AggSum([locn, dateid],
    (TMP_SUM1(long)[][locn, dateid, ksn]<Local> * V_subcategory_I1(long)[][ksn]<Local>)
  );

DECLARE MAP TMP_SUM3(long)[][locn: int] :=
  AggSum([locn],
    (TMP_SUM2(long)[][locn, dateid]<Local> * V_rain_W1(long)[][locn, dateid]<Local>)
  );

DECLARE MAP TMP_SUM4(long)[][locn: int, zip: int] :=
  AggSum([locn, zip],
    (DELTA LOCATION)(locn, zip, rgn_cd, clim_zn_nbr, tot_area_sq_ft, sell_area_sq_ft, avghhi, supertargetdistance, supertargetdrivetime, targetdistance, targetdrivetime, walmartdistance, walmartdrivetime, walmartsupercenterdistance, walmartsupercenterdrivetime)
  );

DECLARE MAP TMP_SUM5(long)[][locn: int] :=
  AggSum([locn],
    (TMP_SUM4(long)[][locn, zip]<Local> * V_population_C1(long)[][zip]<Local>)
  );

DECLARE MAP TMP_SUM6(long)[][zip: int] :=
  AggSum([zip],
    (DELTA CENSUS)(zip, population, white, asian, pacific, blackafrican, medianage, occupiedhouseunits, houseunits, families, households, husbwife, males, females, householdschildren, hispanic)
  );

DECLARE MAP TMP_SUM7(long)[][locn: int] :=
  AggSum([locn],
    (TMP_SUM6(long)[][zip]<Local> * V_rgn_cd_L1(long)[][locn, zip]<Local>)
  );

DECLARE MAP TMP_SUM8(long)[][ksn: int] :=
  AggSum([ksn],
    (DELTA ITEM)(ksn, subcategory, category, categoryCluster, prize)
  );

DECLARE MAP TMP_SUM9(long)[][locn: int, dateid: int] :=
  AggSum([locn, dateid],
    (TMP_SUM8(long)[][ksn]<Local> * V_inventoryunits_I1(long)[][locn, dateid, ksn]<Local>)
  );

DECLARE MAP TMP_SUM10(long)[][locn: int] :=
  AggSum([locn],
    (TMP_SUM9(long)[][locn, dateid]<Local> * V_rain_W1(long)[][locn, dateid]<Local>)
  );

DECLARE MAP TMP_SUM11(long)[][locn: int, dateid: int] :=
  AggSum([locn, dateid],
    (DELTA WEATHER)(locn, dateid, rain, snow, maxtemp, mintemp, meanwind, thunder)
  );

DECLARE MAP TMP_SUM12(long)[][locn: int] :=
  AggSum([locn],
    (TMP_SUM11(long)[][locn, dateid]<Local> * V_ksn_II1(long)[][locn, dateid]<Local>)
  );

-------------------- QUERIES --------------------
DECLARE QUERY V_locn_IIWLC1 := V_locn_IIWLC1(long)[][]<Local>;

------------------- TRIGGERS --------------------
ON BATCH UPDATE OF INVENTORY {
  TMP_SUM1(long)[][locn, dateid, ksn]<Local>  :=  AggSum([locn, dateid, ksn],
    (((DELTA INVENTORY)(locn, dateid, ksn, inventoryunits) ) )
  );
  TMP_SUM2(long)[][locn, dateid]<Local>  :=  AggSum([locn, dateid],
    (TMP_SUM1(long)[][locn, dateid, ksn]<Local> * V_subcategory_I1(long)[][ksn]<Local>)
  );
  TMP_SUM3(long)[][locn]<Local>  :=  AggSum([locn],
    (TMP_SUM2(long)[][locn, dateid]<Local> * V_rain_W1(long)[][locn, dateid]<Local>)
  );
  V_locn_IIWLC1(long)[][]<Local>  +=  AggSum([],
    (TMP_SUM3(long)[][locn]<Local> * V_zip_LC1(long)[][locn]<Local>)
  );
  V_dateid_IIW1(long)[][locn]<Local>  +=  TMP_SUM3(long)[][locn]<Local>;
  V_ksn_II1(long)[][locn, dateid]<Local>  +=  TMP_SUM2(long)[][locn, dateid]<Local>;
  V_inventoryunits_I1(long)[][locn, dateid, ksn]<Local>  +=  TMP_SUM1(long)[][locn, dateid, ksn]<Local>;
}

ON SYSTEM READY {
   V_subcategory_I1(long)[][ksn]<Local>  :=  AggSum([ksn],
    ITEM(ksn, subcategory, category, categoryCluster, prize)
  );
  V_rain_W1(long)[][locn, dateid]<Local>  :=  AggSum([locn, dateid],
    WEATHER(locn, dateid, rain, snow, maxtemp, mintemp, meanwind, thunder)
  );
  V_zip_LC1(long)[][locn]<Local>  :=  AggSum([locn],
    (LOCATION(locn, zip, rgn_cd, clim_zn_nbr, tot_area_sq_ft, sell_area_sq_ft, avghhi, supertargetdistance, supertargetdrivetime, targetdistance, targetdrivetime, walmartdistance, walmartdrivetime, walmartsupercenterdistance, walmartsupercenterdrivetime) * AggSum([zip],
      CENSUS(zip, population, white, asian, pacific, blackafrican, medianage, occupiedhouseunits, houseunits, families, households, husbwife, males, females, householdschildren, hispanic)
    ))
  ); 
}
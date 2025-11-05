from variable_order import Relation

Inventory = Relation(
    "Inventory",
    {"locn": "int", "dateid": "int", "ksn": "int", "inventoryunits": "int"},
    {"locn", "dateid", "ksn"},
)
Location = Relation(
    "Location",
    {
        "locn": "int",
        "zip": "int",
        "rgn_cd": "int",
        "clim_zn_nbr": "int",
        "tot_area_sq_ft": "int",
        "sell_area_sq_ft": "int",
        "avghhi": "int",
        "supertargetdistance": "double",
        "supertargetdrivetime": "double",
        "targetdistance": "double",
        "targetdrivetime": "double",
        "walmartdistance": "double",
        "walmartdrivetime": "double",
        "walmartsupercenterdistance": "double",
        "walmartsupercenterdrivetime": "double",
    },
    {"locn"},
)
Census = Relation(
    "Census",
    {
        "zip": "int",
        "population": "int",
        "white": "int",
        "asian": "int",
        "pacific": "int",
        "blackafrican": "int",
        "medianage": "double",
        "occupiedhouseunits": "int",
        "houseunits": "int",
        "families": "int",
        "households": "int",
        "husbwife": "int",
        "males": "int",
        "females": "int",
        "householdschildren": "int",
        "hispanic": "int",
    },
    {"zip"},
)
Item = Relation(
    "Item",
    {
        "ksn": "int",
        "subcategory": "byte",
        "category": "byte",
        "categoryCluster": "byte",
        "prize": "double",
    },
    {"ksn"},
)
Weather = Relation(
    "Weather",
    {
        "locn": "int",
        "dateid": "int",
        "rain": "byte",
        "snow": "byte",
        "maxtemp": "int",
        "mintemp": "int",
        "meanwind": "double",
        "thunder": "byte",
    },
    {"locn", "dateid"},
)

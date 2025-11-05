import sys
from typing import List

from variable_order import (
    Relation,
    VariableOrderNode,
    generate_txt,
    visualize_node,
    generate_sql_text,
    generate_application_text,
    generate_sql_stream_text,
)
from data_schema import (
    Title,
    Company_Type,
    Info_Type,
    Movie_Companies,
    Movie_Info_Idx,
    CAST_INFO,
    NAME,
    MOVIE_KEYWORD,
    KEYWORD,
)

import tpch_schema as tpch


from retailer_schema import Inventory, Location, Census, Item, Weather


def jobs_query_0():

    movie_id = VariableOrderNode("movie_id")
    company_id = VariableOrderNode("company_id")

    movie_id.add_child(company_id)

    relations = [Title, Movie_Companies]

    free_vars = {}

    return (movie_id, relations, free_vars)


def jobs_query_1():

    movie_id = VariableOrderNode("movie_id")
    company_id = VariableOrderNode("company_id")
    company_type_id = VariableOrderNode("company_type_id")
    info_type_id = VariableOrderNode("info_type_id")

    movie_id.add_child(company_id)
    company_id.add_child(company_type_id)
    movie_id.add_child(info_type_id)

    relations = [Title, Company_Type, Info_Type, Movie_Companies, Movie_Info_Idx]

    free_vars = {}

    return (movie_id, relations, free_vars)


def jobs_query_1_vo1():

    movie_id = VariableOrderNode("movie_id")
    company_id = VariableOrderNode("company_id")
    company_type_id = VariableOrderNode("company_type_id")
    info_type_id = VariableOrderNode("info_type_id")

    company_type_id.add_child(movie_id)
    movie_id.add_child(info_type_id)
    root = company_type_id

    relations = [Title, Company_Type, Info_Type, Movie_Companies, Movie_Info_Idx]

    free_vars = {}

    return (root, relations, free_vars)


def jobs_query_1_vo2():

    movie_id = VariableOrderNode("movie_id")
    company_id = VariableOrderNode("company_id")
    company_type_id = VariableOrderNode("company_type_id")
    info_type_id = VariableOrderNode("info_type_id")

    info_type_id.add_child(movie_id)
    movie_id.add_child(company_type_id)
    root = info_type_id

    relations = [Title, Company_Type, Info_Type, Movie_Companies, Movie_Info_Idx]

    free_vars = {}

    return (root, relations, free_vars)


def jobs_query_1_vo3():

    movie_id = VariableOrderNode("movie_id")
    company_id = VariableOrderNode("company_id")
    company_type_id = VariableOrderNode("company_type_id")
    info_type_id = VariableOrderNode("info_type_id")

    company_type_id.add_child(info_type_id)
    info_type_id.add_child(movie_id)
    root = company_type_id

    relations = [Title, Company_Type, Info_Type, Movie_Companies, Movie_Info_Idx]

    free_vars = {}

    return (root, relations, free_vars)


def jobs_query_2_vo0():

    movie_id = VariableOrderNode("movie_id")
    person_id = VariableOrderNode("person_id")
    keyword_id = VariableOrderNode("keyword_id")

    movie_id.add_child(person_id)
    movie_id.add_child(keyword_id)
    root = movie_id

    relations = [Title, CAST_INFO, NAME, MOVIE_KEYWORD, KEYWORD]

    free_vars = {}

    return (root, relations, free_vars)


def jobs_query_2_vo1():

    movie_id = VariableOrderNode("movie_id")
    person_id = VariableOrderNode("person_id")
    keyword_id = VariableOrderNode("keyword_id")

    person_id.add_child(movie_id)
    movie_id.add_child(keyword_id)
    root = person_id

    relations = [Title, CAST_INFO, NAME, MOVIE_KEYWORD, KEYWORD]

    free_vars = {}

    return (root, relations, free_vars)


def jobs_query_2_vo2():

    movie_id = VariableOrderNode("movie_id")
    person_id = VariableOrderNode("person_id")
    keyword_id = VariableOrderNode("keyword_id")

    keyword_id.add_child(movie_id)
    movie_id.add_child(person_id)
    root = keyword_id

    relations = [Title, CAST_INFO, NAME, MOVIE_KEYWORD, KEYWORD]

    free_vars = {}

    return (root, relations, free_vars)


def jobs_query_2_vo3():

    movie_id = VariableOrderNode("movie_id")
    person_id = VariableOrderNode("person_id")
    keyword_id = VariableOrderNode("keyword_id")

    person_id.add_child(keyword_id)
    keyword_id.add_child(movie_id)
    root = person_id

    relations = [Title, CAST_INFO, NAME, MOVIE_KEYWORD, KEYWORD]

    free_vars = {}

    return (root, relations, free_vars)


def retailer_query_0():
    locn = VariableOrderNode("locn")
    dateid = VariableOrderNode("dateid")
    ksn = VariableOrderNode("ksn")
    zip = VariableOrderNode("zip")

    locn.add_child(dateid)
    dateid.add_child(ksn)
    locn.add_child(zip)
    root = locn

    relations = [Inventory, Location, Census, Item, Weather]

    free_vars = {}

    return (root, relations, free_vars)


def retailer_query_1():
    locn = VariableOrderNode("locn")
    dateid = VariableOrderNode("dateid")
    ksn = VariableOrderNode("ksn")
    zip = VariableOrderNode("zip")

    dateid.add_child(locn)
    locn.add_child(zip)
    locn.add_child(ksn)
    root = dateid

    relations = [Inventory, Location, Census, Item, Weather]

    free_vars = {}

    return (root, relations, free_vars)


def retailer_query_2():
    locn = VariableOrderNode("locn")
    dateid = VariableOrderNode("dateid")
    ksn = VariableOrderNode("ksn")
    zip = VariableOrderNode("zip")

    ksn.add_child(locn)
    locn.add_child(zip)
    locn.add_child(dateid)
    root = ksn

    relations = [Inventory, Location, Census, Item, Weather]

    free_vars = {}

    return (root, relations, free_vars)


def retailer_query_3():
    locn = VariableOrderNode("locn")
    dateid = VariableOrderNode("dateid")
    ksn = VariableOrderNode("ksn")
    zip = VariableOrderNode("zip")

    locn.add_child(dateid)
    dateid.add_child(ksn)
    ksn.add_child(zip)

    root = locn

    relations = [Inventory, Location, Census, Item, Weather]

    free_vars = {}

    return (root, relations, free_vars)


def retailer_query_4():
    locn = VariableOrderNode("locn")
    dateid = VariableOrderNode("dateid")
    ksn = VariableOrderNode("ksn")
    zip = VariableOrderNode("zip")

    ksn.add_child(dateid)
    dateid.add_child(locn)
    locn.add_child(zip)
    root = ksn

    relations = [Inventory, Location, Census, Item, Weather]

    free_vars = {}

    return (root, relations, free_vars)


def tpch_query_1():
    orderkey = VariableOrderNode("orderkey")
    partkey = VariableOrderNode("partkey")
    suppkey = VariableOrderNode("suppkey")

    partkey.add_child(suppkey)
    suppkey.add_child(orderkey)

    root = suppkey

    relations = [tpch.Orders, tpch.Lineitem, tpch.PartSupp, tpch.Part, tpch.Supplier]

    free_vars = {}

    return (root, relations, free_vars)


def main(args):

    is_sql = args[0] if len(args) > 0 else "vo"

    # root, relations, free_vars = retailer_query_4()
    # root, relations, free_vars = jobs_query_1_vo3()
    # root, relations, free_vars = jobs_query_1()

    root, relations, free_vars = tpch_query_1()

    if is_sql == "sql":
        res = generate_sql_stream_text(
            relations, root, free_vars, "1", "imdb", "RingFactorizedRelation"
        )
    else:
        res = generate_txt(relations, root, free_vars)

    visualize_node(root)

    # query_group = args[0] # prefix of the query name
    # q = args[1] # query name
    # path = args[2] # path to dataset
    # is_sql = args[3]
    # ring = args[4]
    # # if args has 5 elements, then we are redirecting the output to a file
    # redirect = len(args) == 6

    # path_len = int(q.split("-")[0][1:])
    # # path_len = int(q[1:])

    # root, relations, free_vars = generate_path_query(path_len)

    # res = ""

    # ring_txt = ""
    # if ring == "factorized":
    #     ring_txt = "RingFactorizedRelation"
    # elif ring == "listing":
    #     ring_txt = "RingRelation"

    # if is_sql == "sql":
    #     res = generate_sql_text(relations, root, free_vars, query_group, q, path, ring_txt)
    # elif is_sql == "vo":
    #     res = generate_txt(relations, root, free_vars)
    # elif is_sql == "app":
    #     res = generate_application_text(relations, query_group, q, path)

    # res += "\n"

    # if not redirect:
    #     visualize_node(root)

    # return res

    pass


if __name__ == "__main__":
    # Pass the command-line arguments (excluding the script name) to the main function
    main(sys.argv[1:])

import sys
from typing import List

from variable_order import Relation, VariableOrderNode, generate_txt, visualize_node, generate_sql_text, generate_application_text, generate_sql_stream_text
from data_schema import Title, Company_Type, Info_Type, Movie_Companies, Movie_Info_Idx

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
    

def main(args):

    is_sql = args[0] if len(args) > 0 else "vo"

    root, relations, free_vars = jobs_query_0()

    if is_sql == "sql":
        res = generate_sql_stream_text(relations, root, free_vars, "1", "imdb", "RingFactorizedRelation")
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

from variable_order import Relation, VariableOrderNode

Title = Relation(
    "Title",
    {
        "movie_id": "INT",
        "t_title": "VARCHAR(100)",
        "t_imdb_index": "VARCHAR(12)",
        "kind_id": "INT",
        "t_production_year": "INT",
        "imdb_id": "INT",
        "t_phonetic_code": "VARCHAR(5)",
        "t_episode_of_id": "INT",
        "t_season_nr": "INT",
        "t_episode_nr": "INT",
        "t_series_years": "VARCHAR(49)",
        "t_md5sum": "VARCHAR(32)",
    },
    {},
)

Company_Type = Relation(
    "Company_Type", {"company_type_id": "INT", "ct_kind": "VARCHAR(32)"}, {}
)

Info_Type = Relation("Info_Type", {"info_type_id": "INT", "it_info": "VARCHAR(32)"}, {})

Movie_Companies = Relation(
    "Movie_Companies",
    {
        "mc_id": "INT",
        "movie_id": "INT",
        "company_id": "INT",
        "company_type_id": "INT",
        "mc_note": "VARCHAR(32)",
    },
    {},
)

Movie_Info_Idx = Relation(
    "Movie_Info_Idx",
    {
        "mii_id": "INT",
        "movie_id": "INT",
        "info_type_id": "INT",
        "mii_info": "VARCHAR(32)",
        "mii_note": "VARCHAR(32)",
    },
    {},
)

CAST_INFO = Relation(
    "CAST_INFO",
    {
        "ci_id": "INT",
        "person_id": "INT",
        "movie_id": "INT",
        "person_role_id": "INT",
        "ci_note": "VARCHAR(100)",
        "ci_nr_order": "INT",
        "role_id": "INT",
    },
    {},
)

NAME = Relation(
    "NAME",
    {
        "person_id": "INT",
        "name": "VARCHAR(100)",
        "n_imdb_index": "VARCHAR(12)",
        "n_imdb_id": "INT",
        "n_gender": "VARCHAR(1)",
        "n_name_pcode_cf": "VARCHAR(5)",
        "n_name_pcode_nf": "VARCHAR(5)",
        "n_surname_pcode": "VARCHAR(5)",
        "n_md5sum": "VARCHAR(32)",
    },
    {},
)

MOVIE_KEYWORD = Relation(
    "MOVIE_KEYWORD", {"mk_id": "INT", "movie_id": "INT", "keyword_id": "INT"}, {}
)

KEYWORD = Relation(
    "KEYWORD",
    {"keyword_id": "INT", "keyword": "VARCHAR(100)", "k_phonetic_code": "VARCHAR(5)"},
    {},
)

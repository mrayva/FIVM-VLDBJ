#ifndef APPLICATION_JOBS_Q1_BASE_HPP
#define APPLICATION_JOBS_Q1_BASE_HPP

#include "../application.hpp"

const string dataPath = "data/imdb";

void Application::init_relations() {
    clear_relations();

    // title
    #if defined(RELATION_TITLE_STATIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<TITLE_entry>(
                "title", dataPath + "/title.csv", '|', true,
                [](dbtoaster::data_t& data) {
                    return [&](TITLE_entry& t) {
                        data.on_insert_TITLE(t);
                    };
                }
        )));
    #elif defined(RELATION_TITLE_DYNAMIC) && defined(BATCH_SIZE)
        typedef const std::vector<DELTA_TITLE_entry>::iterator CIteratorTitle;
        relations.push_back(std::unique_ptr<IRelation>(
            new BatchDispatchableRelation<DELTA_TITLE_entry>(
                "title", dataPath + "/title.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](CIteratorTitle& begin, CIteratorTitle& end) {
                        data.on_batch_update_TITLE(begin, end);
                    };
                }
        )));
    #elif defined(RELATION_TITLE_DYNAMIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<TITLE_entry>(
                "title", dataPath + "/title.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](TITLE_entry& t) {
                        data.on_insert_TITLE(t);
                    };
                }
        )));
    #endif

    // cast_info
    #if defined(RELATION_CAST_INFO_STATIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<CAST_INFO_entry>(
                "cast_info", dataPath + "/cast_info.csv", '|', true,
                [](dbtoaster::data_t& data) {
                    return [&](CAST_INFO_entry& t) {
                        data.on_insert_CAST_INFO(t);
                    };
                }
        )));
    #elif defined(RELATION_CAST_INFO_DYNAMIC) && defined(BATCH_SIZE)
        typedef const std::vector<DELTA_CAST_INFO_entry>::iterator CIteratorCast_info;
        relations.push_back(std::unique_ptr<IRelation>(
            new BatchDispatchableRelation<DELTA_CAST_INFO_entry>(
                "cast_info", dataPath + "/cast_info.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](CIteratorCast_info& begin, CIteratorCast_info& end) {
                        data.on_batch_update_CAST_INFO(begin, end);
                    };
                }
        )));
    #elif defined(RELATION_CAST_INFO_DYNAMIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<CAST_INFO_entry>(
                "cast_info", dataPath + "/cast_info.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](CAST_INFO_entry& t) {
                        data.on_insert_CAST_INFO(t);
                    };
                }
        )));
    #endif


    // name
    #if defined(RELATION_NAME_STATIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<NAME_entry>(
                "name", dataPath + "/name.csv", '|', true,
                [](dbtoaster::data_t& data) {
                    return [&](NAME_entry& t) {
                        data.on_insert_NAME(t);
                    };
                }
        )));
    #elif defined(RELATION_NAME_DYNAMIC) && defined(BATCH_SIZE)
        typedef const std::vector<DELTA_NAME_entry>::iterator CIteratorName;
        relations.push_back(std::unique_ptr<IRelation>(
            new BatchDispatchableRelation<DELTA_NAME_entry>(
                "name", dataPath + "/name.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](CIteratorName& begin, CIteratorName& end) {
                        data.on_batch_update_NAME(begin, end);
                    };
                }
        )));
    #elif defined(RELATION_NAME_DYNAMIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<NAME_entry>(
                "name", dataPath + "/name.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](NAME_entry& t) {
                        data.on_insert_NAME(t);
                    };
                }
        )));
    #endif

    // movie_keyword
    #if defined(RELATION_MOVIE_KEYWORD_STATIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<MOVIE_KEYWORD_entry>(
                "movie_keyword", dataPath + "/movie_keyword.csv", '|', true,
                [](dbtoaster::data_t& data) {
                    return [&](MOVIE_KEYWORD_entry& t) {
                        data.on_insert_MOVIE_KEYWORD(t);
                    };
                }
        )));
    #elif defined(RELATION_MOVIE_KEYWORD_DYNAMIC) && defined(BATCH_SIZE)
        typedef const std::vector<DELTA_MOVIE_KEYWORD_entry>::iterator CIteratorMovie_keyword;
        relations.push_back(std::unique_ptr<IRelation>(
            new BatchDispatchableRelation<DELTA_MOVIE_KEYWORD_entry>(
                "movie_keyword", dataPath + "/movie_keyword.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](CIteratorMovie_keyword& begin, CIteratorMovie_keyword& end) {
                        data.on_batch_update_MOVIE_KEYWORD(begin, end);
                    };
                }
        )));
    #elif defined(RELATION_MOVIE_KEYWORD_DYNAMIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<MOVIE_KEYWORD_entry>(
                "movie_keyword", dataPath + "/movie_keyword.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](MOVIE_KEYWORD_entry& t) {
                        data.on_insert_MOVIE_KEYWORD(t);
                    };
                }
        )));
    #endif

    // keyword
    #if defined(RELATION_KEYWORD_STATIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<KEYWORD_entry>(
                "keyword", dataPath + "/keyword.csv", '|', true,
                [](dbtoaster::data_t& data) {
                    return [&](KEYWORD_entry& t) {
                        data.on_insert_KEYWORD(t);
                    };
                }
        )));
    #elif defined(RELATION_KEYWORD_DYNAMIC) && defined(BATCH_SIZE)
        typedef const std::vector<DELTA_KEYWORD_entry>::iterator CIteratorKeyword;
        relations.push_back(std::unique_ptr<IRelation>(
            new BatchDispatchableRelation<DELTA_KEYWORD_entry>(
                "keyword", dataPath + "/keyword.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](CIteratorKeyword& begin, CIteratorKeyword& end) {
                        data.on_batch_update_KEYWORD(begin, end);
                    };
                }
        )));
    #elif defined(RELATION_KEYWORD_DYNAMIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<KEYWORD_entry>(
                "keyword", dataPath + "/keyword.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](KEYWORD_entry& t) {
                        data.on_insert_KEYWORD(t);
                    };
                }
        )));
    #endif

}	



void Application::on_snapshot(dbtoaster::data_t& data) {
    on_end_processing(data, false);
}

void Application::on_begin_processing(dbtoaster::data_t& data) {

}

void Application::on_end_processing(dbtoaster::data_t& data, bool print_result) {
    if (print_result) {
        data.serialize(std::cout, 0);
    }
}



#endif /* APPLICATION_JOBS_Q1_BASE_HPP */


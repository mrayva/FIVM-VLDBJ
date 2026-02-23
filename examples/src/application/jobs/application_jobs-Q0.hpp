#ifndef APPLICATION_JOBS_Q0_BASE_HPP
#define APPLICATION_JOBS_Q0_BASE_HPP

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


    // movie_companies
    #if defined(RELATION_MOVIE_COMPANIES_STATIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<MOVIE_COMPANIES_entry>(
                "movie_companies", dataPath + "/movie_companies.csv", '|', true,
                [](dbtoaster::data_t& data) {
                    return [&](MOVIE_COMPANIES_entry& t) {
                        data.on_insert_MOVIE_COMPANIES(t);
                    };
                }
        )));
    #elif defined(RELATION_MOVIE_COMPANIES_DYNAMIC) && defined(BATCH_SIZE)
        typedef const std::vector<DELTA_MOVIE_COMPANIES_entry>::iterator CIteratorMovie_companies;
        relations.push_back(std::unique_ptr<IRelation>(
            new BatchDispatchableRelation<DELTA_MOVIE_COMPANIES_entry>(
                "movie_companies", dataPath + "/movie_companies.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](CIteratorMovie_companies& begin, CIteratorMovie_companies& end) {
                        data.on_batch_update_MOVIE_COMPANIES(begin, end);
                    };
                }
        )));
    #elif defined(RELATION_MOVIE_COMPANIES_DYNAMIC)
        relations.push_back(std::unique_ptr<IRelation>(
            new EventDispatchableRelation<MOVIE_COMPANIES_entry>(
                "movie_companies", dataPath + "/movie_companies.csv", '|', false,
                [](dbtoaster::data_t& data) {
                    return [&](MOVIE_COMPANIES_entry& t) {
                        data.on_insert_MOVIE_COMPANIES(t);
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



#endif /* APPLICATION_JOBS_Q0_BASE_HPP */


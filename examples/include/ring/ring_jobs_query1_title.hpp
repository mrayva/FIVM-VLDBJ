#ifndef JOBS1TITLERING_HPP
#define JOBS1TITLERING_HPP

#include "types.hpp"
#include "serialization.hpp"
#include "ring_jobs_query1_movie_companies.hpp"

using namespace dbtoaster;

struct Jobs1TitleRing {
    STRING_TYPE movie_title; // MIN(t.title)
    int movie_year; // MIN(t.production_year)

    explicit Jobs1TitleRing() : movie_title(""), movie_year(0) { }
    explicit Jobs1TitleRing(const STRING_TYPE& _movie_title, int _movie_year)
        : movie_title(_movie_title), movie_year(_movie_year) { }
        
    inline bool isZero() const { 
        return movie_title == "" && movie_year == 0;
    }

    Jobs1TitleRing& operator+=(const Jobs1TitleRing &r) {
        this->movie_title = (this->movie_title < r.movie_title ? this->movie_title : r.movie_title);
        this->movie_year = (this->movie_year < r.movie_year ? this->movie_year : r.movie_year);
        return *this;
    }

    RingJobs1 operator*(const Jobs1MovieCompaniesRing &other) {
        return RingJobs1(
            other.production_note,
            this->movie_title,
            this->movie_year
        );
    }

    // the multiplicity doesn't matter here
    Jobs1TitleRing operator*(long int alpha) const {
        return Jobs1TitleRing(
            this->movie_title,
            this->movie_year
        );
    }

    template<class Archive>
    void serialize(Archive& ar, const unsigned int version) const {
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, movie_title);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, movie_year);
    }
}


Jobs1TitleRing operator*(long int alpha, const Jobs1TitleRing &r) {
    return Jobs1TitleRing(r.movie_title, r.movie_year);
}

// Jobs1TitleRing Ulifttitles(int movie_year, const STRING_TYPE& title) {
//     return Jobs1TitleRing(title, movie_year);
// }

#endif /* RINGJOBS1_HPP */
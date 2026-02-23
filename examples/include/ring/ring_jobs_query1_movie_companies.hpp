#ifndef JOBS1MOVIECOMAPNIESRING_HPP
#define JOBS1MOVIECOMAPNIESRING_HPP

#include "types.hpp"
#include "serialization.hpp"
#include "ring_jobs_query1_title.hpp"

using namespace dbtoaster;

struct Jobs1MovieCompaniesRing {
    STRING_TYPE production_note; // MIN(mc.note)

    explicit Jobs1MovieCompaniesRing() : production_note("") 
    explicit Jobs1MovieCompaniesRing(const STRING_TYPE& _production_note)
        : production_note(_production_note) { }
        
    inline bool isZero() const { 
        return production_note == ""; 
    }

    Jobs1MovieCompaniesRing& operator+=(const Jobs1MovieCompaniesRing &r) {
        this->production_note = (this->production_note < r.production_note ? this->production_note : r.production_note);
        return *this;
    }

    RingJobs1 operator*(const Jobs1TitleRing &other) {
        return RingJobs1(
            this->production_note,
            other.movie_title,
            other.movie_year
        );
    }

    // the multiplicity doesn't matter here
    Jobs1MovieCompaniesRing operator*(long int alpha) const {
        return Jobs1MovieCompaniesRing(
            this->production_note
        );
    }

    template<class Archive>
    void serialize(Archive& ar, const unsigned int version) const {
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, production_note);
    }
};

Jobs1MovieCompaniesRing operator*(long int alpha, const Jobs1MovieCompaniesRing &r) {
    return Jobs1MovieCompaniesRing(r.production_note);
}

// Jobs1MovieCompaniesRing Uliftmoviecompanies(const STRING_TYPE& production_note) {
//     return Jobs1MovieCompaniesRing(production_note);
// }

#endif /* JOBS1MOVIECOMAPNIESRING_HPP */
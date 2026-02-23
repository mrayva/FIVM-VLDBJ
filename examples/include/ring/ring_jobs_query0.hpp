#ifndef RINGJOBS1_HPP
#define RINGJOBS1_HPP

#include <limits>
#include <algorithm>

#include "types.hpp"
#include "serialization.hpp"

// define the one and zero elements of the min integer semiring
#define MIN_INTEGER_ONE std::numeric_limits<int>::max()
#define MIN_INTEGER_ZERO -1

using namespace dbtoaster;

struct RingJobs1
{

    // const int MIN_INTEGER_ONE = std::numeric_limits<int>::max();
    // const int MIN_INTEGER_ZERO = -1;

    size_t count_movie_title_1a;
    size_t count_movie_title_1b;
    size_t count_movie_title_1c;
    size_t count_movie_title_1d;

    int min_movie_year_1a;
    int min_movie_year_1b;
    int min_movie_year_1c;
    int min_movie_year_1d;

    size_t count_production_note_1a;
    size_t count_production_note_1b;
    size_t count_production_note_1c;
    size_t count_production_note_1d;

    explicit RingJobs1() : count_movie_title_1a(0), count_movie_title_1b(0), count_movie_title_1c(0), count_movie_title_1d(0), min_movie_year_1a(MIN_INTEGER_ZERO), min_movie_year_1b(MIN_INTEGER_ZERO), min_movie_year_1c(MIN_INTEGER_ZERO), min_movie_year_1d(MIN_INTEGER_ZERO), count_production_note_1a(0), count_production_note_1b(0), count_production_note_1c(0), count_production_note_1d(0) {}

    explicit RingJobs1(size_t count_movie_title_1a, size_t count_movie_title_1b, size_t count_movie_title_1c, size_t count_movie_title_1d, int min_movie_year_1a, int min_movie_year_1b, int min_movie_year_1c, int min_movie_year_1d,
                       size_t count_production_note_1a, size_t count_production_note_1b, size_t count_production_note_1c, size_t count_production_note_1d)
        : count_movie_title_1a(count_movie_title_1a), count_movie_title_1b(count_movie_title_1b), count_movie_title_1c(count_movie_title_1c), count_movie_title_1d(count_movie_title_1d), min_movie_year_1a(min_movie_year_1a), min_movie_year_1b(min_movie_year_1b), min_movie_year_1c(min_movie_year_1c), min_movie_year_1d(min_movie_year_1d), count_production_note_1a(count_production_note_1a), count_production_note_1b(count_production_note_1b), count_production_note_1c(count_production_note_1c), count_production_note_1d(count_production_note_1d) {}

    inline bool isZero() const
    {
        return count_movie_title_1a == 0 && count_movie_title_1b == 0 && count_movie_title_1c == 0 && count_movie_title_1d == 0 && min_movie_year_1a == MIN_INTEGER_ZERO && min_movie_year_1b == MIN_INTEGER_ZERO && min_movie_year_1c == MIN_INTEGER_ZERO && min_movie_year_1d == MIN_INTEGER_ZERO && count_production_note_1a == 0 && count_production_note_1b == 0 && count_production_note_1c == 0 && count_production_note_1d == 0;
    }

    RingJobs1 &operator+=(const RingJobs1 &r)
    {
        this->count_movie_title_1a += r.count_movie_title_1a;
        this->count_movie_title_1b += r.count_movie_title_1b;
        this->count_movie_title_1c += r.count_movie_title_1c;
        this->count_movie_title_1d += r.count_movie_title_1d;

        this->min_movie_year_1a = this->min_movie_year_1a == MIN_INTEGER_ZERO ? r.min_movie_year_1a : (r.min_movie_year_1a == MIN_INTEGER_ZERO ? this->min_movie_year_1a : std::min(this->min_movie_year_1a, r.min_movie_year_1a));
        this->min_movie_year_1b = this->min_movie_year_1b == MIN_INTEGER_ZERO ? r.min_movie_year_1b : (r.min_movie_year_1b == MIN_INTEGER_ZERO ? this->min_movie_year_1b : std::min(this->min_movie_year_1b, r.min_movie_year_1b));
        this->min_movie_year_1c = this->min_movie_year_1c == MIN_INTEGER_ZERO ? r.min_movie_year_1c : (r.min_movie_year_1c == MIN_INTEGER_ZERO ? this->min_movie_year_1c : std::min(this->min_movie_year_1c, r.min_movie_year_1c));
        this->min_movie_year_1d = this->min_movie_year_1d == MIN_INTEGER_ZERO ? r.min_movie_year_1d : (r.min_movie_year_1d == MIN_INTEGER_ZERO ? this->min_movie_year_1d : std::min(this->min_movie_year_1d, r.min_movie_year_1d));

        this->count_production_note_1a += r.count_production_note_1a;
        this->count_production_note_1b += r.count_production_note_1b;
        this->count_production_note_1c += r.count_production_note_1c;
        this->count_production_note_1d += r.count_production_note_1d;

        return *this;
    }

    RingJobs1 operator*(const RingJobs1 &other)
    {
        if (this->min_movie_year_1a == 1880 || other.min_movie_year_1a == 1880)
            std::cout << "min_movie_year_1a = " << this->min_movie_year_1a << ", other.min_movie_year_1a = " << other.min_movie_year_1a << std::endl;

        return RingJobs1(
            this->count_movie_title_1a * other.count_movie_title_1a,
            this->count_movie_title_1b * other.count_movie_title_1b,
            this->count_movie_title_1c * other.count_movie_title_1c,
            this->count_movie_title_1d * other.count_movie_title_1d,

            (this->min_movie_year_1a == MIN_INTEGER_ZERO || other.min_movie_year_1a == MIN_INTEGER_ZERO) ? MIN_INTEGER_ZERO : std::min(this->min_movie_year_1a, other.min_movie_year_1a),
            (this->min_movie_year_1b == MIN_INTEGER_ZERO || other.min_movie_year_1b == MIN_INTEGER_ZERO) ? MIN_INTEGER_ZERO : std::min(this->min_movie_year_1b, other.min_movie_year_1b),
            (this->min_movie_year_1c == MIN_INTEGER_ZERO || other.min_movie_year_1c == MIN_INTEGER_ZERO) ? MIN_INTEGER_ZERO : std::min(this->min_movie_year_1c, other.min_movie_year_1c),
            (this->min_movie_year_1d == MIN_INTEGER_ZERO || other.min_movie_year_1d == MIN_INTEGER_ZERO) ? MIN_INTEGER_ZERO : std::min(this->min_movie_year_1d, other.min_movie_year_1d),

            this->count_production_note_1a * other.count_production_note_1a,
            this->count_production_note_1b * other.count_production_note_1b,
            this->count_production_note_1c * other.count_production_note_1c,
            this->count_production_note_1d * other.count_production_note_1d);
    }

    RingJobs1 operator*(long int alpha) const
    {
        return RingJobs1(
            this->count_movie_title_1a * alpha,
            this->count_movie_title_1b * alpha,
            this->count_movie_title_1c * alpha,
            this->count_movie_title_1d * alpha,

            // the multiplicity doesn't matter here
            this->min_movie_year_1a,
            this->min_movie_year_1b,
            this->min_movie_year_1c,
            this->min_movie_year_1d,

            this->count_production_note_1a * alpha,
            this->count_production_note_1b * alpha,
            this->count_production_note_1c * alpha,
            this->count_production_note_1d * alpha);
    }

    template <class Archive>
    void serialize(Archive &ar, const unsigned int version) const
    {
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_movie_title_1a);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_movie_title_1b);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_movie_title_1c);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_movie_title_1d);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, min_movie_year_1a);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, min_movie_year_1b);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, min_movie_year_1c);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, min_movie_year_1d);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_production_note_1a);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_production_note_1b);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_production_note_1c);
        ar << ELEM_SEPARATOR;
        DBT_SERIALIZATION_NVP(ar, count_production_note_1d);
    }
};

RingJobs1 operator*(long int alpha, const RingJobs1 &r)
{
    return RingJobs1(
        alpha * r.count_movie_title_1a,
        alpha * r.count_movie_title_1b,
        alpha * r.count_movie_title_1c,
        alpha * r.count_movie_title_1d,

        r.min_movie_year_1a,
        r.min_movie_year_1b,
        r.min_movie_year_1c,
        r.min_movie_year_1d,

        alpha * r.count_production_note_1a,
        alpha * r.count_production_note_1b,
        alpha * r.count_production_note_1c,
        alpha * r.count_production_note_1d);
}

RingJobs1 Ulifttitles(int movie_year)
{
    bool cond_1a = true; // 1a has no condition on movie_year
    bool cond_1b = movie_year >= 2005 && movie_year <= 2010;
    bool cond_1c = movie_year > 2010;
    bool cond_1d = movie_year > 2000;

    return RingJobs1(
        cond_1a ? 1 : 0,
        cond_1b ? 1 : 0,
        cond_1c ? 1 : 0,
        cond_1d ? 1 : 0,
        cond_1a ? movie_year : -1,
        cond_1b ? movie_year : -1,
        cond_1c ? movie_year : -1,
        cond_1d ? movie_year : -1,
        cond_1a ? 1 : 0,
        cond_1b ? 1 : 0,
        cond_1c ? 1 : 0,
        cond_1d ? 1 : 0);
}

RingJobs1 Uliftmoviecompanies(const STRING_TYPE &production_note)
{
    bool is_null = production_note == "-1";

    bool cond_1 = !is_null && production_note.find("(as Metro-Goldwyn-Mayer Pictures)") == std::string::npos;
    bool cond_2 = !is_null && production_note.find("(co-production)") != std::string::npos;
    bool cond_3 = !is_null && production_note.find("(presents)") != std::string::npos;

    bool cond_1a = cond_1 && (cond_2 || cond_3);
    bool cond_1b = cond_1;
    bool cond_1c = cond_1 && cond_2;
    bool cond_1d = cond_1;

    return RingJobs1(
        cond_1a ? 1 : 0,
        cond_1b ? 1 : 0,
        cond_1c ? 1 : 0,
        cond_1d ? 1 : 0,

        cond_1a ? MIN_INTEGER_ONE : MIN_INTEGER_ZERO,
        cond_1b ? MIN_INTEGER_ONE : MIN_INTEGER_ZERO,
        cond_1c ? MIN_INTEGER_ONE : MIN_INTEGER_ZERO,
        cond_1d ? MIN_INTEGER_ONE : MIN_INTEGER_ZERO,

        cond_1a ? 1 : 0,
        cond_1b ? 1 : 0,
        cond_1c ? 1 : 0,
        cond_1d ? 1 : 0);
}

#endif /* RINGJOBS1_HPP */
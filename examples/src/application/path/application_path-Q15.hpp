#ifndef APPLICATION_PATH_Q15_BASE_HPP
#define APPLICATION_PATH_Q15_BASE_HPP

#include "../application.hpp"

const string dataPath = "data/snap";

void Application::init_relations() {
	clear_relations();

#if defined(RELATION_R1_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R1_entry>(
            "R1", dataPath + "/R1.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R1_entry& t) {
                    data.on_insert_R1(t);
                };
            }
    )));
#elif defined(RELATION_R1_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R1_entry>::iterator CIteratorR1;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R1_entry>(
            "R1", dataPath + "/R1.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR1& begin, CIteratorR1& end) {
                    data.on_batch_update_R1(begin, end);
                };
            }
    )));
#elif defined(RELATION_R1_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R1_entry>(
            "R1", dataPath + "/R1.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R1_entry& t) {
                    data.on_insert_R1(t);
                };
            }
    )));
#endif
#if defined(RELATION_R2_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R2_entry>(
            "R2", dataPath + "/R2.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R2_entry& t) {
                    data.on_insert_R2(t);
                };
            }
    )));
#elif defined(RELATION_R2_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R2_entry>::iterator CIteratorR2;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R2_entry>(
            "R2", dataPath + "/R2.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR2& begin, CIteratorR2& end) {
                    data.on_batch_update_R2(begin, end);
                };
            }
    )));
#elif defined(RELATION_R2_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R2_entry>(
            "R2", dataPath + "/R2.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R2_entry& t) {
                    data.on_insert_R2(t);
                };
            }
    )));
#endif
#if defined(RELATION_R3_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R3_entry>(
            "R3", dataPath + "/R3.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R3_entry& t) {
                    data.on_insert_R3(t);
                };
            }
    )));
#elif defined(RELATION_R3_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R3_entry>::iterator CIteratorR3;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R3_entry>(
            "R3", dataPath + "/R3.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR3& begin, CIteratorR3& end) {
                    data.on_batch_update_R3(begin, end);
                };
            }
    )));
#elif defined(RELATION_R3_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R3_entry>(
            "R3", dataPath + "/R3.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R3_entry& t) {
                    data.on_insert_R3(t);
                };
            }
    )));
#endif
#if defined(RELATION_R4_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R4_entry>(
            "R4", dataPath + "/R4.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R4_entry& t) {
                    data.on_insert_R4(t);
                };
            }
    )));
#elif defined(RELATION_R4_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R4_entry>::iterator CIteratorR4;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R4_entry>(
            "R4", dataPath + "/R4.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR4& begin, CIteratorR4& end) {
                    data.on_batch_update_R4(begin, end);
                };
            }
    )));
#elif defined(RELATION_R4_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R4_entry>(
            "R4", dataPath + "/R4.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R4_entry& t) {
                    data.on_insert_R4(t);
                };
            }
    )));
#endif
#if defined(RELATION_R5_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R5_entry>(
            "R5", dataPath + "/R5.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R5_entry& t) {
                    data.on_insert_R5(t);
                };
            }
    )));
#elif defined(RELATION_R5_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R5_entry>::iterator CIteratorR5;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R5_entry>(
            "R5", dataPath + "/R5.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR5& begin, CIteratorR5& end) {
                    data.on_batch_update_R5(begin, end);
                };
            }
    )));
#elif defined(RELATION_R5_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R5_entry>(
            "R5", dataPath + "/R5.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R5_entry& t) {
                    data.on_insert_R5(t);
                };
            }
    )));
#endif
#if defined(RELATION_R6_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R6_entry>(
            "R6", dataPath + "/R6.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R6_entry& t) {
                    data.on_insert_R6(t);
                };
            }
    )));
#elif defined(RELATION_R6_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R6_entry>::iterator CIteratorR6;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R6_entry>(
            "R6", dataPath + "/R6.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR6& begin, CIteratorR6& end) {
                    data.on_batch_update_R6(begin, end);
                };
            }
    )));
#elif defined(RELATION_R6_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R6_entry>(
            "R6", dataPath + "/R6.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R6_entry& t) {
                    data.on_insert_R6(t);
                };
            }
    )));
#endif
#if defined(RELATION_R7_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R7_entry>(
            "R7", dataPath + "/R7.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R7_entry& t) {
                    data.on_insert_R7(t);
                };
            }
    )));
#elif defined(RELATION_R7_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R7_entry>::iterator CIteratorR7;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R7_entry>(
            "R7", dataPath + "/R7.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR7& begin, CIteratorR7& end) {
                    data.on_batch_update_R7(begin, end);
                };
            }
    )));
#elif defined(RELATION_R7_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R7_entry>(
            "R7", dataPath + "/R7.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R7_entry& t) {
                    data.on_insert_R7(t);
                };
            }
    )));
#endif
#if defined(RELATION_R8_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R8_entry>(
            "R8", dataPath + "/R8.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R8_entry& t) {
                    data.on_insert_R8(t);
                };
            }
    )));
#elif defined(RELATION_R8_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R8_entry>::iterator CIteratorR8;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R8_entry>(
            "R8", dataPath + "/R8.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR8& begin, CIteratorR8& end) {
                    data.on_batch_update_R8(begin, end);
                };
            }
    )));
#elif defined(RELATION_R8_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R8_entry>(
            "R8", dataPath + "/R8.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R8_entry& t) {
                    data.on_insert_R8(t);
                };
            }
    )));
#endif
#if defined(RELATION_R9_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R9_entry>(
            "R9", dataPath + "/R9.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R9_entry& t) {
                    data.on_insert_R9(t);
                };
            }
    )));
#elif defined(RELATION_R9_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R9_entry>::iterator CIteratorR9;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R9_entry>(
            "R9", dataPath + "/R9.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR9& begin, CIteratorR9& end) {
                    data.on_batch_update_R9(begin, end);
                };
            }
    )));
#elif defined(RELATION_R9_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R9_entry>(
            "R9", dataPath + "/R9.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R9_entry& t) {
                    data.on_insert_R9(t);
                };
            }
    )));
#endif
#if defined(RELATION_R10_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R10_entry>(
            "R10", dataPath + "/R10.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R10_entry& t) {
                    data.on_insert_R10(t);
                };
            }
    )));
#elif defined(RELATION_R10_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R10_entry>::iterator CIteratorR10;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R10_entry>(
            "R10", dataPath + "/R10.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR10& begin, CIteratorR10& end) {
                    data.on_batch_update_R10(begin, end);
                };
            }
    )));
#elif defined(RELATION_R10_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R10_entry>(
            "R10", dataPath + "/R10.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R10_entry& t) {
                    data.on_insert_R10(t);
                };
            }
    )));
#endif
#if defined(RELATION_R11_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R11_entry>(
            "R11", dataPath + "/R11.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R11_entry& t) {
                    data.on_insert_R11(t);
                };
            }
    )));
#elif defined(RELATION_R11_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R11_entry>::iterator CIteratorR11;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R11_entry>(
            "R11", dataPath + "/R11.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR11& begin, CIteratorR11& end) {
                    data.on_batch_update_R11(begin, end);
                };
            }
    )));
#elif defined(RELATION_R11_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R11_entry>(
            "R11", dataPath + "/R11.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R11_entry& t) {
                    data.on_insert_R11(t);
                };
            }
    )));
#endif
#if defined(RELATION_R12_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R12_entry>(
            "R12", dataPath + "/R12.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R12_entry& t) {
                    data.on_insert_R12(t);
                };
            }
    )));
#elif defined(RELATION_R12_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R12_entry>::iterator CIteratorR12;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R12_entry>(
            "R12", dataPath + "/R12.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR12& begin, CIteratorR12& end) {
                    data.on_batch_update_R12(begin, end);
                };
            }
    )));
#elif defined(RELATION_R12_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R12_entry>(
            "R12", dataPath + "/R12.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R12_entry& t) {
                    data.on_insert_R12(t);
                };
            }
    )));
#endif
#if defined(RELATION_R13_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R13_entry>(
            "R13", dataPath + "/R13.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R13_entry& t) {
                    data.on_insert_R13(t);
                };
            }
    )));
#elif defined(RELATION_R13_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R13_entry>::iterator CIteratorR13;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R13_entry>(
            "R13", dataPath + "/R13.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR13& begin, CIteratorR13& end) {
                    data.on_batch_update_R13(begin, end);
                };
            }
    )));
#elif defined(RELATION_R13_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R13_entry>(
            "R13", dataPath + "/R13.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R13_entry& t) {
                    data.on_insert_R13(t);
                };
            }
    )));
#endif
#if defined(RELATION_R14_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R14_entry>(
            "R14", dataPath + "/R14.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R14_entry& t) {
                    data.on_insert_R14(t);
                };
            }
    )));
#elif defined(RELATION_R14_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R14_entry>::iterator CIteratorR14;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R14_entry>(
            "R14", dataPath + "/R14.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR14& begin, CIteratorR14& end) {
                    data.on_batch_update_R14(begin, end);
                };
            }
    )));
#elif defined(RELATION_R14_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R14_entry>(
            "R14", dataPath + "/R14.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R14_entry& t) {
                    data.on_insert_R14(t);
                };
            }
    )));
#endif
#if defined(RELATION_R15_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R15_entry>(
            "R15", dataPath + "/R15.tbl", '|', true,
            [](dbtoaster::data_t& data) {
                return [&](R15_entry& t) {
                    data.on_insert_R15(t);
                };
            }
    )));
#elif defined(RELATION_R15_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_R15_entry>::iterator CIteratorR15;
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_R15_entry>(
            "R15", dataPath + "/R15.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](CIteratorR15& begin, CIteratorR15& end) {
                    data.on_batch_update_R15(begin, end);
                };
            }
    )));
#elif defined(RELATION_R15_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<R15_entry>(
            "R15", dataPath + "/R15.tbl", '|', false,
            [](dbtoaster::data_t& data) {
                return [&](R15_entry& t) {
                    data.on_insert_R15(t);
                };
            }
    )));
#endif

}	void Application::on_snapshot(dbtoaster::data_t& data) {
		on_end_processing(data, false);
	}

	void Application::on_begin_processing(dbtoaster::data_t& data) {

	}

	void Application::on_end_processing(dbtoaster::data_t& data, bool print_result) {
		if (print_result) {
			data.serialize(std::cout, 0);
		}
	}



#endif /* APPLICATION_PATH_Q15_BASE_HPP */


#ifndef APPLICATION_TPCH_QUERY9_HPP
#define APPLICATION_TPCH_QUERY9_HPP

#include <iostream>
#include "application.hpp"

class TpchQuery9Application : public Application {
 public:
  void onSnapshot(const dbtoaster::data_t& data) override {
    onEndProcessing(data, false);
  }

  void onBeginProcessing(const dbtoaster::data_t& data) override {}

  void onEndProcessing(const dbtoaster::data_t& data,
                       bool print_result) override {
    if (print_result) {
      data.serialize(std::cout, 0);
    }
  }
};

std::unique_ptr<Application> createApplication() {
  return std::make_unique<TpchQuery9Application>();
}

#endif /* APPLICATION_TPCH_QUERY9_HPP */

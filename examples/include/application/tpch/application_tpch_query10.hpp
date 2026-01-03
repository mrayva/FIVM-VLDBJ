#ifndef APPLICATION_TPCH_QUERY10_HPP
#define APPLICATION_TPCH_QUERY10_HPP

#include <iostream>
#include "application.hpp"

class TpchQuery10Application : public Application {
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
  return std::make_unique<TpchQuery10Application>();
}

#endif /* APPLICATION_TPCH_QUERY10_HPP */

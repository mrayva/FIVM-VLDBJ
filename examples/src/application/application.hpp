#ifndef APPLICATION_HPP
#define APPLICATION_HPP

#include "dispatcher.hpp"
#include "relation.hpp"
#include "stopwatch.hpp"
#include <iostream>
#include <vector>

using namespace dbtoaster;

class Application {
protected:
  std::vector<std::unique_ptr<IRelation>> relations;
  Multiplexer static_multiplexer;
  Multiplexer dynamic_multiplexer;
  Stopwatch stream_start_time;
  long cumulative_stream_time;

  void init_relations();

  void load_relations();

  void clear_relations();

  void init_dispatchers(dbtoaster::data_t &data);

  void clear_dispatchers();

  void process_tables(dbtoaster::data_t &data);

  void process_on_system_ready(dbtoaster::data_t &data);

  void process_streams(dbtoaster::data_t &data);

  void process_streams_snapshot(dbtoaster::data_t &data,
                                long snapshot_interval);

  void process_streams_no_snapshot(dbtoaster::data_t &data);

  void on_snapshot(dbtoaster::data_t &data);

  void report_snapshot_elapsed_time(dbtoaster::data_t &data);

  void on_begin_processing(dbtoaster::data_t &data);

  void on_end_processing(dbtoaster::data_t &data, bool print_result);

  void print_result(dbtoaster::data_t &data);

public:
  Application() {}

  ~Application() {
    clear_relations();
    clear_dispatchers();
  }

  void run(size_t num_of_runs, bool output_result);
};

void Application::load_relations() {
  for (auto &r : relations) {
    r->clear();
    r->load();
  }
}

void Application::clear_relations() {
  for (auto &r : relations) {
    r->clear();
  }
  relations.clear();
}

void Application::init_dispatchers(dbtoaster::data_t &data) {
  clear_dispatchers();

  for (auto &r : relations) {
    if (r->is_static()) {
      static_multiplexer.add_dispatcher(r->create_dispatcher(data));
    } else {
      dynamic_multiplexer.add_dispatcher(r->create_dispatcher(data));
    }
  }
}

void Application::clear_dispatchers() {
  static_multiplexer.clear();
  dynamic_multiplexer.clear();
}

void Application::report_snapshot_elapsed_time(dbtoaster::data_t &data) {
  stream_start_time.stop();
  long elapsed_time = stream_start_time.elapsedTimeInMilliSeconds();
  cumulative_stream_time += elapsed_time;
  std::cout << "Processed: " << data.tN
            << "    Elapsed time: " << cumulative_stream_time << " ms"
            << std::endl;
  stream_start_time.restart();
}

void Application::process_tables(dbtoaster::data_t &data) {
  while (static_multiplexer.has_next()) {
    static_multiplexer.next();
  }
}

void Application::process_on_system_ready(dbtoaster::data_t &data) {
  data.on_system_ready_event();
}

void Application::process_streams(dbtoaster::data_t &data) {
  // Hardcoded snapshot interval: 10,000 tuples
  const long SNAPSHOT_INTERVAL = 10000;
  process_streams_snapshot(data, SNAPSHOT_INTERVAL);
}

void Application::process_streams_snapshot(dbtoaster::data_t &data,
                                           long snapshot_interval) {
  long next_snapshot = 0;
  cumulative_stream_time = 0;
  stream_start_time.restart();

  while (dynamic_multiplexer.has_next()) {
    dynamic_multiplexer.next();

    if (data.tN >= next_snapshot) {
      on_snapshot(data);
      next_snapshot = data.tN + snapshot_interval;
    }
  }

  if (next_snapshot != data.tN + snapshot_interval) {
    on_snapshot(data);
  }
}

void Application::process_streams_no_snapshot(dbtoaster::data_t &data) {
  cumulative_stream_time = 0;
  stream_start_time.restart();
  std::cout << "  " << data.tN << std::endl;

  Stopwatch local_time;
  local_time.restart();

  while (dynamic_multiplexer.has_next()) {
    dynamic_multiplexer.next();
    // std::cout << "  " << data.tN << std::endl;

    local_time.stop();
    long elapsed_time = local_time.elapsedTimeInMilliSeconds();

    // if the elapsed time is greater than 4 hours
    if (elapsed_time > 14400000) {
      std::cout << "Processed: " << data.tN << std::endl;
      exit(0);
    }
  }
}

void Application::run(size_t num_of_runs, bool print_result) {
  std::cout << "-------------" << std::endl;

  init_relations();

  Stopwatch local_time, total_time;

  std::cout << "Loading input relations... " << std::flush;
  local_time.restart();
  load_relations();
  local_time.stop();
  std::cout << local_time.elapsedTimeInMilliSeconds() << " ms" << std::endl;
  for (auto &r : relations) {
    std::cout << "  " << r->get_name() << " (" << r->size() << ") "
              << std::endl;
  }

  for (size_t run = 0; run < num_of_runs; run++) {

    dbtoaster::data_t data;

    std::cout << "-------------" << std::endl;

    init_dispatchers(data);

    std::cout << "1. On begin of processing... " << std::flush;
    local_time.restart();
    on_begin_processing(data);
    local_time.stop();
    std::cout << local_time.elapsedTimeInMilliSeconds() << " ms" << std::endl;

    std::cout << "2. Processing tables... " << std::flush;
    local_time.restart();
    process_tables(data);
    local_time.stop();
    std::cout << local_time.elapsedTimeInMilliSeconds() << " ms" << std::endl;

    total_time.restart();

    std::cout << "3. On system ready... " << std::flush;
    local_time.restart();
    process_on_system_ready(data);
    local_time.stop();
    std::cout << local_time.elapsedTimeInMilliSeconds() << " ms" << std::endl;

    std::cout << "4. Processing streams... " << std::flush;
    ;
    local_time.restart();
    process_streams(data);
    local_time.stop();
    std::cout << local_time.elapsedTimeInMilliSeconds() << " ms" << std::endl;

    std::cout << "5. On end of processing... " << std::flush;
    local_time.restart();
    on_end_processing(data, print_result);
    local_time.stop();
    std::cout << local_time.elapsedTimeInMilliSeconds() << " ms" << std::endl;

    total_time.stop();

    std::cout << "    Run: " << run << "    Processed: " << data.tN
              << "    Skipped: " << data.tS << "    Execution time: "
              << total_time.elapsedTimeInMilliSeconds() << " ms"
#ifdef BATCH_SIZE
              << "    Batch size: " << BATCH_SIZE
#endif
              << std::endl
              << "-------------" << std::endl;

    clear_dispatchers();
  }

  clear_relations();
}

#endif /* APPLICATION_HPP */
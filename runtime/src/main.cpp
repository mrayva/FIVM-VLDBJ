#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <string>
#include <stdexcept>

class Application;
std::unique_ptr<Application> createApplication();

namespace {

void print_usage(const char* prog) {
  std::cout
      << "Usage: " << prog << " [options]\n\n"
      << "Options:\n"
      << "  -r, --num-runs <count>    Number of runs (default: 1)\n"
      << "  -b, --batch-size <size>   Batch size for input reads (default: 1000)\n"
      << "      --no-output           Suppress final result serialization\n"
      << "  -h, --help                Show this help message\n";
}

int parse_positive_int(const char* arg_name, const char* value) {
  char* end = nullptr;
  long parsed = std::strtol(value, &end, 10);
  if (end == value || *end != '\0' || parsed <= 0) {
    throw std::invalid_argument(std::string("Invalid value for ") + arg_name +
                                ": " + value);
  }
  return static_cast<int>(parsed);
}

}  // namespace

int main(int argc, char** argv) {
  try {
    int opt_num_runs = 1;
    size_t opt_batch_size = 1000;
    bool opt_print_result = true;
    auto require_value = [&](int index) -> const char* {
      if (index + 1 >= argc) {
        throw std::invalid_argument(std::string("Missing value for ") + argv[index]);
      }
      return argv[index + 1];
    };

    for (int i = 1; i < argc; i++) {
      if (strcmp(argv[i], "--num-runs") == 0 || strcmp(argv[i], "-r") == 0) {
        opt_num_runs = parse_positive_int(argv[i], require_value(i));
        ++i;
        continue;
      }
      if (strcmp(argv[i], "--batch-size") == 0 || strcmp(argv[i], "-b") == 0) {
        opt_batch_size =
            static_cast<size_t>(parse_positive_int(argv[i], require_value(i)));
        ++i;
        continue;
      }
      if (strcmp(argv[i], "--no-output") == 0) {
        opt_print_result = false;
        continue;
      }
      if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
        print_usage(argv[0]);
        return 0;
      }
      throw std::invalid_argument(std::string("Unknown argument: ") + argv[i]);
    }

#ifndef __APPLE__
    cpu_set_t mask;
    CPU_ZERO(&mask);
    CPU_SET(0, &mask);
    sched_setaffinity(0, sizeof(mask), &mask);
#endif

    std::unique_ptr<Application> app = createApplication();
    app->run(opt_num_runs, opt_print_result, opt_batch_size);

    return 0;
  } catch (const std::invalid_argument& e) {
    std::cerr << "Error: " << e.what() << "\n\n";
    print_usage(argv[0]);
    return 1;
  } catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << "\n";
    return 1;
  }
}

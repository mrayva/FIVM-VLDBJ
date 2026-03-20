#ifndef RUNTIME_CSV_READER_HPP
#define RUNTIME_CSV_READER_HPP

#include <fstream>
#include <sstream>
#include <stdexcept>

#include "data_source.hpp"

// ---------------------------------------------------------------------------
class CsvReader : public IDataChunkReader {
 public:
  CsvReader(const DataSourceConfig& c, size_t batch_sz)
      : cfg(c),
        ifs(c.uri),
        delimiter(parseDelimiter(c)),
        batch_size(batch_sz),
        line_number(0) {
    if (!ifs.is_open()) {
      throw std::runtime_error("Cannot open CSV file: " + c.uri);
    }
    // Avoid skipping whitespace
    ifs >> std::noskipws;
  }

  std::shared_ptr<DataChunk> next() override {
    if (!has_next()) return nullptr;

    auto chunk = std::make_shared<DataChunk>(cfg);
    std::string line;
    size_t count = 0;

    while (count < batch_size && std::getline(ifs, line)) {
      ++line_number;
      if (line.empty()) continue;

      std::stringstream ss(line);
      parse_line_into_chunk(ss, *chunk, line);
      ++count;
    }
    chunk->row_count = count;

    return (count > 0) ? std::move(chunk) : nullptr;
  }

  bool has_next() override { return ifs.good(); }

  void reset() override {
    ifs.clear();   // Clear eof/fail bits
    ifs.seekg(0);  // Go back to start

    // Avoid skipping whitespace
    ifs >> std::noskipws;
    line_number = 0;
  }

 protected:
  const DataSourceConfig cfg;
  std::ifstream ifs;
  char delimiter;
  size_t batch_size;
  size_t line_number;

  static char parseDelimiter(const DataSourceConfig& c) {
    auto it = c.options.find("delimiter");
    const std::string& del = (it != c.options.end()) ? it->second : ",";

    if (del.size() != 1) {
      throw std::invalid_argument("Invalid delimiter: " + del);
    }
    return del[0];
  }

  [[noreturn]] void fail_parse(const std::string& msg,
                               const std::string& line) const {
    throw std::runtime_error("CSV parse error in '" + cfg.uri + "' at line " +
                             std::to_string(line_number) + ": " + msg +
                             " | line='" + line + "'");
  }

  void parse_line_into_chunk(std::stringstream& ss,
                             DataChunk& chunk,
                             const std::string& line) {
    // Stream the line as CSV fields
    std::string field;

    for (size_t i = 0; i < cfg.schema.size(); ++i) {
      if (!getline(ss, field, delimiter)) {
        fail_parse("Missing value for column '" + cfg.schema[i].name + "'",
                   line);
      }
      try {
        chunk.cols[i]->append_from_string(field, cfg.schema[i].name);
      } catch (const std::exception& e) {
        fail_parse(e.what(), line);
      }
    }

    payload_t payload = 1;
    if (getline(ss, field, delimiter)) {
      try {
        payload = parse<payload_t>(field);
      } catch (const std::exception& e) {
        fail_parse(std::string("Invalid payload value: '") + field + "' (" +
                       e.what() + ")",
                   line);
      }
    }

    if (getline(ss, field, delimiter)) {
      fail_parse("Unexpected extra field after payload: '" + field + "'", line);
    }

    chunk.payload.push_back(payload);
  }
};

class CsvReaderPredefinedBatches : public CsvReader {
 public:
  CsvReaderPredefinedBatches(const DataSourceConfig& c, size_t batch_sz)
      : CsvReader(c, batch_sz) {}

  std::shared_ptr<DataChunk> next() override {
    if (!has_next()) return nullptr;

    auto chunk = std::make_shared<DataChunk>(cfg);
    std::string line;
    size_t count = 0;
    int32_t currBatchId = -1;

    while (count < batch_size) {
      // Save current position
      std::streampos pos = ifs.tellg();

      if (!std::getline(ifs, line)) break;
      ++line_number;

      if (line.empty()) continue;

      std::stringstream ss(line);
      int32_t batchId = get_batch_id(ss, line);

      if (currBatchId == -1) {
        currBatchId = batchId;
      }

      if (currBatchId == batchId) {
        parse_line_into_chunk(ss, *chunk, line);
        ++count;
      } else {
        // Restore the stream to the beginning of this line
        ifs.clear();
        ifs.seekg(pos);
        break;
      }
    }
    chunk->row_count = count;

    return (count > 0) ? std::move(chunk) : nullptr;
  }

 protected:
  int32_t get_batch_id(std::stringstream& ss, const std::string& line) {
    std::string field;
    if (!getline(ss, field, delimiter)) {
      fail_parse("Missing predefined batch id column", line);
    }
    try {
      return parse<int32_t>(field);
    } catch (const std::exception& e) {
      fail_parse(std::string("Invalid predefined batch id: '") + field + "' (" +
                     e.what() + ")",
                 line);
    }
  }
};

#endif /* RUNTIME_CSV_READER_HPP */

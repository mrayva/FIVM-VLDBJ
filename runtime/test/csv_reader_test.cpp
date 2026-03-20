#include <gtest/gtest.h>

#include <filesystem>
#include <fstream>
#include <string>

#include "csv_reader.hpp"

namespace {

namespace fs = std::filesystem;

DataSourceConfig make_config(const std::string& uri,
                             std::vector<SchemaField> schema,
                             std::map<std::string, std::string> options = {}) {
  DataSourceConfig cfg;
  cfg.name = "TEST";
  cfg.isStream = true;
  cfg.type = DataSourceType::CSV;
  cfg.uri = uri;
  cfg.schema = std::move(schema);
  cfg.options = std::move(options);
  return cfg;
}

std::string write_temp_file(const std::string& name, const std::string& contents) {
  const fs::path dir = fs::temp_directory_path() / "fivm-csv-reader-tests";
  fs::create_directories(dir);
  const fs::path path = dir / name;
  std::ofstream out(path);
  out << contents;
  out.close();
  return path.string();
}

std::string read_failure(CsvReader& reader) {
  try {
    (void)reader.next();
    ADD_FAILURE() << "expected CsvReader::next() to throw";
    return "";
  } catch (const std::runtime_error& e) {
    return e.what();
  }
}

std::string read_predefined_failure(CsvReaderPredefinedBatches& reader) {
  try {
    (void)reader.next();
    ADD_FAILURE() << "expected CsvReaderPredefinedBatches::next() to throw";
    return "";
  } catch (const std::runtime_error& e) {
    return e.what();
  }
}

TEST(CsvReaderTest, ParsesValidRowsAndPayloads) {
  const auto path = write_temp_file("valid.csv", "1,2.5\n2,3.5,7\n");
  CsvReader reader(make_config(
                       path,
                       {{"a", PrimitiveType::INT32}, {"b", PrimitiveType::DOUBLE}}),
                   16);

  auto chunk = reader.next();
  ASSERT_NE(chunk, nullptr);
  ASSERT_EQ(chunk->row_count, 2U);
  EXPECT_EQ(chunk->payload.size(), 2U);
  EXPECT_EQ(chunk->payload[0], 1);
  EXPECT_EQ(chunk->payload[1], 7);

  auto* col_a = static_cast<Column<int32_t>*>(chunk->cols[0].get());
  auto* col_b = static_cast<Column<double>*>(chunk->cols[1].get());
  ASSERT_EQ(col_a->data.size(), 2U);
  ASSERT_EQ(col_b->data.size(), 2U);
  EXPECT_EQ(col_a->data[0], 1);
  EXPECT_DOUBLE_EQ(col_b->data[1], 3.5);
}

TEST(CsvReaderTest, RejectsMissingField) {
  const auto path = write_temp_file("missing.csv", "1\n");
  CsvReader reader(make_config(
                       path,
                       {{"a", PrimitiveType::INT32}, {"b", PrimitiveType::DOUBLE}}),
                   16);

  const std::string err = read_failure(reader);
  EXPECT_NE(err.find("Missing value for column 'b'"), std::string::npos);
  EXPECT_NE(err.find("line 1"), std::string::npos);
}

TEST(CsvReaderTest, RejectsExtraFieldAfterPayload) {
  const auto path = write_temp_file("extra.csv", "1,2.5,3,unexpected\n");
  CsvReader reader(make_config(
                       path,
                       {{"a", PrimitiveType::INT32}, {"b", PrimitiveType::DOUBLE}}),
                   16);

  const std::string err = read_failure(reader);
  EXPECT_NE(err.find("Unexpected extra field after payload"), std::string::npos);
  EXPECT_NE(err.find("unexpected"), std::string::npos);
}

TEST(CsvReaderTest, RejectsInvalidNumericField) {
  const auto path = write_temp_file("invalid_numeric.csv", "1,oops\n");
  CsvReader reader(make_config(
                       path,
                       {{"a", PrimitiveType::INT32}, {"b", PrimitiveType::FLOAT}}),
                   16);

  const std::string err = read_failure(reader);
  EXPECT_NE(err.find("Invalid float value for column 'b'"), std::string::npos);
  EXPECT_NE(err.find("'oops'"), std::string::npos);
}

TEST(CsvReaderTest, RejectsInvalidPayload) {
  const auto path = write_temp_file("invalid_payload.csv", "1,2.5,abc\n");
  CsvReader reader(make_config(
                       path,
                       {{"a", PrimitiveType::INT32}, {"b", PrimitiveType::DOUBLE}}),
                   16);

  const std::string err = read_failure(reader);
  EXPECT_NE(err.find("Invalid payload value: 'abc'"), std::string::npos);
}

TEST(CsvReaderTest, RejectsInvalidPredefinedBatchId) {
  const auto path = write_temp_file("invalid_batch.csv", "oops,1,2.5\n");
  CsvReaderPredefinedBatches reader(
      make_config(path,
                  {{"a", PrimitiveType::INT32}, {"b", PrimitiveType::DOUBLE}},
                  {{"predefined_batches", "true"}}),
      16);

  const std::string err = read_predefined_failure(reader);
  EXPECT_NE(err.find("Invalid predefined batch id: 'oops'"), std::string::npos);
}

}  // namespace

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

#ifndef FIVM_ZERIALIZE_INPUT_ADAPTOR_HPP
#define FIVM_ZERIALIZE_INPUT_ADAPTOR_HPP

#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "../common.hpp"
#include "../data_source.hpp"
#include "format.hpp"
#include "message.hpp"
#include "queue.hpp"

// Zerialize protocol headers
#include <zerialize/protocols/msgpack.hpp>
#include <zerialize/protocols/cbor.hpp>
#include <zerialize/protocols/flex.hpp>
#include <zerialize/protocols/zera.hpp>
#include <zerialize/protocols/json.hpp>

namespace fivm {
namespace zerialize {

/// Field extractor configuration for schema-driven deserialization
struct FieldMapping {
    std::string name;        // Field name in serialized data
    PrimitiveType type;      // Target column type
    size_t column_index;     // Index in DataChunk::cols
    bool required = false;   // If true, missing field is an error
};

/// Input adaptor that reads ZerializeMessages from a queue,
/// deserializes them, and produces DataChunks for FIVM processing.
///
/// Usage:
///   auto queue = make_message_queue(10000);
///   ZerializeInputAdaptor adaptor(config, queue, 1000);
///   while (auto chunk = adaptor.next()) {
///       process(chunk);
///   }
class ZerializeInputAdaptor : public IDataChunkReader {
public:
    /// Construct adaptor with SPSC queue
    ZerializeInputAdaptor(const DataSourceConfig& cfg,
                          MessageQueuePtr queue,
                          size_t batch_size = 1000)
        : cfg_(cfg),
          spsc_queue_(std::move(queue)),
          batch_size_(batch_size),
          closed_(false) {
        build_field_mappings();
    }

    /// Construct adaptor with MPSC queue
    ZerializeInputAdaptor(const DataSourceConfig& cfg,
                          MessageQueueMPSCPtr queue,
                          size_t batch_size = 1000)
        : cfg_(cfg),
          mpsc_queue_(std::move(queue)),
          batch_size_(batch_size),
          closed_(false) {
        build_field_mappings();
    }

    /// Read next batch of messages and return as DataChunk
    DataChunkPtr next() override {
        if (closed_) return nullptr;

        auto chunk = std::make_shared<DataChunk>(cfg_);
        size_t count = 0;
        Message msg;

        while (count < batch_size_) {
            bool got_message = false;

            if (spsc_queue_) {
                got_message = spsc_queue_->try_pop(msg);
            } else if (mpsc_queue_) {
                got_message = mpsc_queue_->try_pop(msg);
            }

            if (!got_message) {
                // No more messages available right now
                break;
            }

            // Check relation matches (or accept all if not specified)
            if (!cfg_.name.empty() && msg.relation != cfg_.name) {
                continue;  // Skip messages for other relations
            }

            // Deserialize based on format
            if (deserialize_message(msg, *chunk)) {
                chunk->payload.push_back(
                    static_cast<payload_t>(msg.multiplicity));
                ++count;
            }
        }

        chunk->row_count = count;
        return (count > 0) ? std::move(chunk) : nullptr;
    }

    /// Check if there might be more data (non-blocking)
    bool has_next() override {
        if (closed_) return false;

        if (spsc_queue_) return !spsc_queue_->empty();
        if (mpsc_queue_) return !mpsc_queue_->empty();
        return false;
    }

    /// Reset is not supported for queue-based sources
    void reset() override {
        throw std::runtime_error(
            "ZerializeInputAdaptor: reset() not supported for queue sources");
    }

    /// Signal that no more messages will arrive
    void close() { closed_ = true; }

    /// Get the data source configuration
    const DataSourceConfig& config() const { return cfg_; }

private:
    DataSourceConfig cfg_;
    MessageQueuePtr spsc_queue_;
    MessageQueueMPSCPtr mpsc_queue_;
    size_t batch_size_;
    std::atomic<bool> closed_;
    std::vector<FieldMapping> field_mappings_;

    /// Build field mappings from schema
    void build_field_mappings() {
        field_mappings_.reserve(cfg_.schema.size());
        for (size_t i = 0; i < cfg_.schema.size(); ++i) {
            field_mappings_.push_back(FieldMapping{
                .name = cfg_.schema[i].name,
                .type = cfg_.schema[i].type,
                .column_index = i,
                .required = false});
        }
    }

    /// Deserialize a message into chunk columns
    /// Returns true if successful
    bool deserialize_message(const Message& msg, DataChunk& chunk) {
        // Dispatch based on format
        // NOTE: This requires zerialize headers to be included by the user.
        // We use a callback-based approach to avoid hard dependency.
        
        switch (msg.format) {
            case Format::MSGPACK:
                return deserialize_msgpack(msg.view(), chunk);
            case Format::CBOR:
                return deserialize_cbor(msg.view(), chunk);
            case Format::FLEXBUFFERS:
                return deserialize_flexbuffers(msg.view(), chunk);
            case Format::ZERA:
                return deserialize_zera(msg.view(), chunk);
            case Format::JSON:
                return deserialize_json(msg.view(), chunk);
        }
        return false;
    }

    // -------------------------------------------------------------------------
    // Format-specific deserializers
    // These are implemented as separate methods for clarity.
    // In production, you'd use zerialize::X::Reader for each format.
    // -------------------------------------------------------------------------

    /// Generic deserialization using a Reader type
    template <typename Reader>
    bool deserialize_generic(std::span<const uint8_t> data, DataChunk& chunk) {
        try {
            Reader reader(data);
            if (!reader.isMap()) return false;

            for (const auto& mapping : field_mappings_) {
                auto field = reader[mapping.name];
                append_field(field, mapping, chunk);
            }
            return true;
        } catch (...) {
            return false;
        }
    }

    /// Append a field value to the appropriate column
    template <typename FieldReader>
    void append_field(const FieldReader& field, const FieldMapping& mapping,
                      DataChunk& chunk) {
        auto* col = chunk.cols[mapping.column_index].get();

        switch (mapping.type) {
            case PrimitiveType::INT8:
                append_int<int8_t>(field, col);
                break;
            case PrimitiveType::INT16:
                append_int<int16_t>(field, col);
                break;
            case PrimitiveType::INT32:
                append_int<int32_t>(field, col);
                break;
            case PrimitiveType::INT64:
                append_int<int64_t>(field, col);
                break;
            case PrimitiveType::FLOAT:
                append_float<float>(field, col);
                break;
            case PrimitiveType::DOUBLE:
                append_float<double>(field, col);
                break;
            case PrimitiveType::STRING:
                append_string(field, col);
                break;
            case PrimitiveType::CHAR:
                append_char(field, col);
                break;
            case PrimitiveType::DATE:
                append_date(field, col);
                break;
        }
    }

    template <typename T, typename FieldReader>
    void append_int(const FieldReader& field, ColumnBase* col) {
        auto* typed_col = static_cast<Column<T>*>(col);
        if (field.isInt() || field.isUInt()) {
            typed_col->data.push_back(static_cast<T>(field.asInt64()));
        } else {
            typed_col->data.push_back(T{});  // Default value
        }
    }

    template <typename T, typename FieldReader>
    void append_float(const FieldReader& field, ColumnBase* col) {
        auto* typed_col = static_cast<Column<T>*>(col);
        if (field.isFloat()) {
            typed_col->data.push_back(static_cast<T>(field.asDouble()));
        } else if (field.isInt() || field.isUInt()) {
            typed_col->data.push_back(static_cast<T>(field.asInt64()));
        } else {
            typed_col->data.push_back(T{});
        }
    }

    template <typename FieldReader>
    void append_string(const FieldReader& field, ColumnBase* col) {
        auto* typed_col = static_cast<Column<string_t>*>(col);
        if (field.isString()) {
            typed_col->data.push_back(string_t(std::string(field.asStringView())));
        } else {
            typed_col->data.push_back(string_t{});
        }
    }

    template <typename FieldReader>
    void append_char(const FieldReader& field, ColumnBase* col) {
        auto* typed_col = static_cast<Column<char>*>(col);
        if (field.isString()) {
            auto sv = field.asStringView();
            typed_col->data.push_back(sv.empty() ? '\0' : sv[0]);
        } else {
            typed_col->data.push_back('\0');
        }
    }

    template <typename FieldReader>
    void append_date(const FieldReader& field, ColumnBase* col) {
        auto* typed_col = static_cast<Column<date_t>*>(col);
        if (field.isString()) {
            typed_col->data.push_back(
                date_t{dbtoaster::str2date(std::string(field.asStringView()).c_str())});
        } else if (field.isInt()) {
            typed_col->data.push_back(date_t{static_cast<int32_t>(field.asInt64())});
        } else {
            typed_col->data.push_back(date_t{0});
        }
    }

    // -------------------------------------------------------------------------
    // Format-specific deserializers using zerialize readers
    // -------------------------------------------------------------------------
    
    bool deserialize_msgpack(std::span<const uint8_t> data, DataChunk& chunk) {
        return deserialize_generic<zerialize::MsgPack::Deserializer>(data, chunk);
    }

    bool deserialize_cbor(std::span<const uint8_t> data, DataChunk& chunk) {
        return deserialize_generic<zerialize::CBOR::Deserializer>(data, chunk);
    }

    bool deserialize_flexbuffers(std::span<const uint8_t> data, DataChunk& chunk) {
        return deserialize_generic<zerialize::Flex::Deserializer>(data, chunk);
    }

    bool deserialize_zera(std::span<const uint8_t> data, DataChunk& chunk) {
        return deserialize_generic<zerialize::Zera::Deserializer>(data, chunk);
    }

    bool deserialize_json(std::span<const uint8_t> data, DataChunk& chunk) {
        return deserialize_generic<zerialize::Json::Deserializer>(data, chunk);
    }
};

}  // namespace zerialize
}  // namespace fivm

#endif  // FIVM_ZERIALIZE_INPUT_ADAPTOR_HPP

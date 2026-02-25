#ifndef FIVM_ZERIALIZE_OUTPUT_ADAPTOR_HPP
#define FIVM_ZERIALIZE_OUTPUT_ADAPTOR_HPP

#include <memory>
#include <stdexcept>
#include <vector>

#include "../common.hpp"
#include "../data_source.hpp"
#include "format.hpp"
#include "message.hpp"
#include "queue.hpp"

namespace fivm {
namespace zerialize {

/// Output adaptor that serializes DataChunks and pushes to a queue.
/// Used for emitting view maintenance results to external consumers.
///
/// Usage:
///   auto queue = make_message_queue(10000);
///   ZerializeOutputAdaptor adaptor(config, queue, Format::MSGPACK);
///   adaptor.push(chunk);
class ZerializeOutputAdaptor : public IDataChunkWriter {
public:
    /// Construct adaptor with SPSC queue
    ZerializeOutputAdaptor(const DataSourceConfig& cfg,
                           MessageQueuePtr queue,
                           Format format = Format::MSGPACK)
        : cfg_(cfg),
          spsc_queue_(std::move(queue)),
          format_(format),
          closed_(false) {}

    /// Construct adaptor with MPSC queue
    ZerializeOutputAdaptor(const DataSourceConfig& cfg,
                           MessageQueueMPSCPtr queue,
                           Format format = Format::MSGPACK)
        : cfg_(cfg),
          mpsc_queue_(std::move(queue)),
          format_(format),
          closed_(false) {}

    /// Serialize and push a DataChunk to the queue.
    /// Each row becomes a separate message.
    void push(DataChunkPtr chunk) override {
        if (!chunk || chunk->row_count == 0) return;
        if (closed_) {
            throw std::runtime_error("ZerializeOutputAdaptor: cannot push after close");
        }

        for (size_t row = 0; row < chunk->row_count; ++row) {
            Message msg = serialize_row(*chunk, row);
            
            if (spsc_queue_) {
                // Spin until we can push (or implement backpressure)
                while (!spsc_queue_->try_push(std::move(msg))) {
                    // Could add yield/sleep here for backpressure
                }
            } else if (mpsc_queue_) {
                mpsc_queue_->push(std::move(msg));
            }
        }
    }

    /// Signal that no more data will be written
    void close() override { closed_ = true; }

    /// Get output format
    Format format() const { return format_; }

    /// Set output format
    void set_format(Format f) { format_ = f; }

private:
    DataSourceConfig cfg_;
    MessageQueuePtr spsc_queue_;
    MessageQueueMPSCPtr mpsc_queue_;
    Format format_;
    std::atomic<bool> closed_;

    /// Serialize a single row from chunk to a Message
    Message serialize_row(const DataChunk& chunk, size_t row_idx) {
        std::vector<uint8_t> data;
        
        switch (format_) {
            case Format::MSGPACK:
                data = serialize_msgpack(chunk, row_idx);
                break;
            case Format::CBOR:
                data = serialize_cbor(chunk, row_idx);
                break;
            case Format::FLEXBUFFERS:
                data = serialize_flexbuffers(chunk, row_idx);
                break;
            case Format::ZERA:
                data = serialize_zera(chunk, row_idx);
                break;
            case Format::JSON:
                data = serialize_json(chunk, row_idx);
                break;
        }

        return Message{
            std::move(data),
            format_,
            cfg_.name,
            static_cast<int64_t>(chunk.payload[row_idx])
        };
    }

    // -------------------------------------------------------------------------
    // Format-specific serializers (stubs - implement with zerialize)
    // -------------------------------------------------------------------------

    std::vector<uint8_t> serialize_msgpack(const DataChunk& chunk, size_t row) {
        // Example implementation structure:
        // zerialize::msgpack::Writer writer;
        // auto map = writer.map(cfg_.schema.size());
        // for (size_t i = 0; i < cfg_.schema.size(); ++i) {
        //     map.key(cfg_.schema[i].name);
        //     write_value(map, chunk.cols[i].get(), row);
        // }
        // return writer.finish();

        // Fallback: simple key=value text format for testing
        return serialize_simple_text(chunk, row);
    }

    std::vector<uint8_t> serialize_cbor(const DataChunk& chunk, size_t row) {
        return serialize_simple_text(chunk, row);  // Stub
    }

    std::vector<uint8_t> serialize_flexbuffers(const DataChunk& chunk, size_t row) {
        return serialize_simple_text(chunk, row);  // Stub
    }

    std::vector<uint8_t> serialize_zera(const DataChunk& chunk, size_t row) {
        return serialize_simple_text(chunk, row);  // Stub
    }

    std::vector<uint8_t> serialize_json(const DataChunk& chunk, size_t row) {
        // Simple JSON serialization
        std::string json = "{";
        
        for (size_t i = 0; i < cfg_.schema.size(); ++i) {
            if (i > 0) json += ",";
            json += "\"" + cfg_.schema[i].name + "\":";
            json += value_to_json(chunk.cols[i].get(), cfg_.schema[i].type, row);
        }
        
        json += "}";
        return std::vector<uint8_t>(json.begin(), json.end());
    }

    /// Fallback text serialization for testing
    std::vector<uint8_t> serialize_simple_text(const DataChunk& chunk, size_t row) {
        std::string text;
        
        for (size_t i = 0; i < cfg_.schema.size(); ++i) {
            if (i > 0) text += "|";
            text += cfg_.schema[i].name + "=";
            text += value_to_string(chunk.cols[i].get(), cfg_.schema[i].type, row);
        }
        
        return std::vector<uint8_t>(text.begin(), text.end());
    }

    /// Convert column value to string
    std::string value_to_string(const ColumnBase* col, PrimitiveType type, size_t row) {
        switch (type) {
            case PrimitiveType::INT8:
                return std::to_string(get_value<int8_t>(col, row));
            case PrimitiveType::INT16:
                return std::to_string(get_value<int16_t>(col, row));
            case PrimitiveType::INT32:
                return std::to_string(get_value<int32_t>(col, row));
            case PrimitiveType::INT64:
                return std::to_string(get_value<int64_t>(col, row));
            case PrimitiveType::FLOAT:
                return std::to_string(get_value<float>(col, row));
            case PrimitiveType::DOUBLE:
                return std::to_string(get_value<double>(col, row));
            case PrimitiveType::CHAR:
                return std::string(1, get_value<char>(col, row));
            case PrimitiveType::STRING: {
                const auto& s = get_value<string_t>(col, row);
                return std::string(s.c_str());
            }
            case PrimitiveType::DATE:
                return std::to_string(get_value<date_t>(col, row).value);
        }
        return "";
    }

    /// Convert column value to JSON
    std::string value_to_json(const ColumnBase* col, PrimitiveType type, size_t row) {
        switch (type) {
            case PrimitiveType::INT8:
            case PrimitiveType::INT16:
            case PrimitiveType::INT32:
            case PrimitiveType::INT64:
            case PrimitiveType::FLOAT:
            case PrimitiveType::DOUBLE:
            case PrimitiveType::DATE:
                return value_to_string(col, type, row);
            case PrimitiveType::CHAR:
            case PrimitiveType::STRING:
                return "\"" + escape_json(value_to_string(col, type, row)) + "\"";
        }
        return "null";
    }

    /// Escape string for JSON
    static std::string escape_json(const std::string& s) {
        std::string result;
        result.reserve(s.size());
        for (char c : s) {
            switch (c) {
                case '"':  result += "\\\""; break;
                case '\\': result += "\\\\"; break;
                case '\n': result += "\\n";  break;
                case '\r': result += "\\r";  break;
                case '\t': result += "\\t";  break;
                default:   result += c;
            }
        }
        return result;
    }

    template <typename T>
    static const T& get_value(const ColumnBase* col, size_t row) {
        return static_cast<const Column<T>*>(col)->data[row];
    }
};

}  // namespace zerialize
}  // namespace fivm

#endif  // FIVM_ZERIALIZE_OUTPUT_ADAPTOR_HPP

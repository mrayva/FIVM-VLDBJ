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

// Zerialize protocol headers
#include <zerialize/protocols/msgpack.hpp>
#include <zerialize/protocols/cbor.hpp>
#include <zerialize/protocols/flex.hpp>
#include <zerialize/protocols/zera.hpp>
#include <zerialize/protocols/json.hpp>

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
    // Format-specific serializers using zerialize writers
    // -------------------------------------------------------------------------

    /// Generic serialization using a Protocol's RootSerializer and Serializer
    template <typename Protocol>
    std::vector<uint8_t> serialize_generic(const DataChunk& chunk, size_t row) {
        typename Protocol::RootSerializer root;
        typename Protocol::Serializer ser(root);
        
        ser.begin_map(cfg_.schema.size());
        for (size_t i = 0; i < cfg_.schema.size(); ++i) {
            ser.key(cfg_.schema[i].name);
            write_value(ser, chunk.cols[i].get(), cfg_.schema[i].type, row);
        }
        ser.end_map();
        
        auto buf = root.finish();
        return std::vector<uint8_t>(buf.data(), buf.data() + buf.size());
    }
    
    /// Write a typed value to the serializer
    template <typename Serializer>
    void write_value(Serializer& ser, const ColumnBase* col, PrimitiveType type, size_t row) {
        switch (type) {
            case PrimitiveType::INT8:
                ser.int64(get_value<int8_t>(col, row));
                break;
            case PrimitiveType::INT16:
                ser.int64(get_value<int16_t>(col, row));
                break;
            case PrimitiveType::INT32:
                ser.int64(get_value<int32_t>(col, row));
                break;
            case PrimitiveType::INT64:
                ser.int64(get_value<int64_t>(col, row));
                break;
            case PrimitiveType::FLOAT:
                ser.double_(get_value<float>(col, row));
                break;
            case PrimitiveType::DOUBLE:
                ser.double_(get_value<double>(col, row));
                break;
            case PrimitiveType::CHAR:
                ser.string(std::string_view(&get_value<char>(col, row), 1));
                break;
            case PrimitiveType::STRING: {
                const auto& s = get_value<string_t>(col, row);
                ser.string(std::string_view(s.c_str(), s.size()));
                break;
            }
            case PrimitiveType::DATE:
                ser.int64(get_value<date_t>(col, row).value);
                break;
        }
    }

    std::vector<uint8_t> serialize_msgpack(const DataChunk& chunk, size_t row) {
        return serialize_generic<zerialize::MsgPack>(chunk, row);
    }

    std::vector<uint8_t> serialize_cbor(const DataChunk& chunk, size_t row) {
        return serialize_generic<zerialize::CBOR>(chunk, row);
    }

    std::vector<uint8_t> serialize_flexbuffers(const DataChunk& chunk, size_t row) {
        return serialize_generic<zerialize::Flex>(chunk, row);
    }

    std::vector<uint8_t> serialize_zera(const DataChunk& chunk, size_t row) {
        return serialize_generic<zerialize::Zera>(chunk, row);
    }

    std::vector<uint8_t> serialize_json(const DataChunk& chunk, size_t row) {
        return serialize_generic<zerialize::Json>(chunk, row);
    }

    template <typename T>
    static const T& get_value(const ColumnBase* col, size_t row) {
        return static_cast<const Column<T>*>(col)->data[row];
    }
};

}  // namespace zerialize
}  // namespace fivm

#endif  // FIVM_ZERIALIZE_OUTPUT_ADAPTOR_HPP

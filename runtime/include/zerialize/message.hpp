#ifndef FIVM_ZERIALIZE_MESSAGE_HPP
#define FIVM_ZERIALIZE_MESSAGE_HPP

#include <cstdint>
#include <span>
#include <string>
#include <utility>
#include <vector>

#include "format.hpp"

namespace fivm {
namespace zerialize {

/// A message containing serialized data for queue transport.
/// This is the element type for lock-free queues between producers and FIVM.
struct Message {
    /// Raw serialized bytes (owns the data)
    std::vector<uint8_t> data;

    /// Serialization format for deserialization dispatch
    Format format = Format::MSGPACK;

    /// Target relation name (e.g., "ORDERS", "LINEITEM")
    std::string relation;

    /// Multiplicity: +1 for insert, -1 for delete, other values for batch weight
    int64_t multiplicity = 1;

    /// Sequence number for ordering (optional, 0 if unused)
    uint64_t sequence = 0;

    // -------------------------------------------------------------------------
    // Constructors
    // -------------------------------------------------------------------------

    Message() = default;

    Message(std::vector<uint8_t> d, Format f, std::string rel, int64_t mult = 1)
        : data(std::move(d)),
          format(f),
          relation(std::move(rel)),
          multiplicity(mult) {}

    // Move-only for efficiency (avoid copying large payloads)
    Message(const Message&) = delete;
    Message& operator=(const Message&) = delete;
    Message(Message&&) noexcept = default;
    Message& operator=(Message&&) noexcept = default;

    // -------------------------------------------------------------------------
    // Accessors
    // -------------------------------------------------------------------------

    /// Zero-copy view of the data
    std::span<const uint8_t> view() const noexcept {
        return {data.data(), data.size()};
    }

    /// Size of serialized data in bytes
    size_t size() const noexcept { return data.size(); }

    /// Check if message is empty
    bool empty() const noexcept { return data.empty(); }

    /// Check if this is an insert (+multiplicity)
    bool is_insert() const noexcept { return multiplicity > 0; }

    /// Check if this is a delete (-multiplicity)
    bool is_delete() const noexcept { return multiplicity < 0; }
};

/// Batch of messages for bulk operations
struct MessageBatch {
    std::vector<Message> messages;
    
    MessageBatch() = default;
    explicit MessageBatch(size_t reserve_size) { messages.reserve(reserve_size); }

    void push(Message&& msg) { messages.push_back(std::move(msg)); }
    size_t size() const noexcept { return messages.size(); }
    bool empty() const noexcept { return messages.empty(); }
    void clear() { messages.clear(); }

    auto begin() { return messages.begin(); }
    auto end() { return messages.end(); }
    auto begin() const { return messages.begin(); }
    auto end() const { return messages.end(); }
};

}  // namespace zerialize
}  // namespace fivm

#endif  // FIVM_ZERIALIZE_MESSAGE_HPP

#ifndef FIVM_ZERIALIZE_HPP
#define FIVM_ZERIALIZE_HPP

/// @file zerialize.hpp
/// @brief Main include for FIVM zerialize adaptors
///
/// This header provides lock-free queue-based input/output adaptors
/// for integrating FIVM with zerialize-compatible serialization formats.
///
/// Supported formats:
///   - MsgPack
///   - CBOR
///   - FlexBuffers
///   - Zera
///   - JSON
///
/// Example usage:
/// @code
///   #include <zerialize.hpp>
///
///   // Create a lock-free queue
///   auto queue = fivm::zerialize::make_message_queue(10000);
///
///   // Producer thread pushes serialized messages
///   queue->try_push(fivm::zerialize::Message{
///       .data = msgpack_bytes,
///       .format = fivm::zerialize::Format::MSGPACK,
///       .relation = "ORDERS",
///       .multiplicity = 1
///   });
///
///   // FIVM consumer reads DataChunks
///   fivm::zerialize::ZerializeInputAdaptor adaptor(config, queue);
///   while (auto chunk = adaptor.next()) {
///       // Process with FIVM triggers
///   }
/// @endcode

#include "zerialize/format.hpp"
#include "zerialize/message.hpp"
#include "zerialize/queue.hpp"
#include "zerialize/input_adaptor.hpp"
#include "zerialize/output_adaptor.hpp"

#endif  // FIVM_ZERIALIZE_HPP

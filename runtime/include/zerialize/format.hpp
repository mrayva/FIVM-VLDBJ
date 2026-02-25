#ifndef FIVM_ZERIALIZE_FORMAT_HPP
#define FIVM_ZERIALIZE_FORMAT_HPP

#include <cstdint>
#include <span>
#include <stdexcept>
#include <string_view>

namespace fivm {
namespace zerialize {

/// Supported serialization formats
enum class Format : uint8_t {
    MSGPACK,      // MessagePack binary format
    CBOR,         // Concise Binary Object Representation
    FLEXBUFFERS,  // Google FlatBuffers' FlexBuffers
    ZERA,         // Zerialize's native format
    JSON          // JSON (text-based, for debugging/interop)
};

/// Convert format enum to string
inline constexpr std::string_view format_name(Format f) noexcept {
    switch (f) {
        case Format::MSGPACK:     return "msgpack";
        case Format::CBOR:        return "cbor";
        case Format::FLEXBUFFERS: return "flexbuffers";
        case Format::ZERA:        return "zera";
        case Format::JSON:        return "json";
    }
    return "unknown";
}

/// Parse format from string (case-insensitive)
inline Format parse_format(std::string_view s) {
    // Convert to lowercase comparison
    auto eq = [](std::string_view a, std::string_view b) {
        if (a.size() != b.size()) return false;
        for (size_t i = 0; i < a.size(); ++i) {
            char ca = (a[i] >= 'A' && a[i] <= 'Z') ? (a[i] + 32) : a[i];
            char cb = (b[i] >= 'A' && b[i] <= 'Z') ? (b[i] + 32) : b[i];
            if (ca != cb) return false;
        }
        return true;
    };

    if (eq(s, "msgpack"))     return Format::MSGPACK;
    if (eq(s, "cbor"))        return Format::CBOR;
    if (eq(s, "flexbuffers")) return Format::FLEXBUFFERS;
    if (eq(s, "flex"))        return Format::FLEXBUFFERS;
    if (eq(s, "zera"))        return Format::ZERA;
    if (eq(s, "json"))        return Format::JSON;

    throw std::invalid_argument("Unknown serialization format: " + std::string(s));
}

/// Attempt to detect format from magic bytes (best-effort)
inline Format detect_format(std::span<const uint8_t> data) {
    if (data.empty()) {
        throw std::invalid_argument("Cannot detect format from empty data");
    }

    uint8_t first = data[0];

    // JSON: starts with '{', '[', '"', or whitespace
    if (first == '{' || first == '[' || first == '"' ||
        first == ' ' || first == '\t' || first == '\n' || first == '\r') {
        return Format::JSON;
    }

    // CBOR: map (0xa0-0xbf) or array (0x80-0x9f) or tagged (0xc0-0xdb)
    // Most common: 0xa0-0xbf (map), 0xbf (indefinite map)
    if ((first >= 0xa0 && first <= 0xbf) || first == 0xbf) {
        return Format::CBOR;
    }

    // MsgPack: fixmap (0x80-0x8f), map16 (0xde), map32 (0xdf)
    //          fixarray (0x90-0x9f), array16 (0xdc), array32 (0xdd)
    if ((first >= 0x80 && first <= 0x9f) ||
        first == 0xdc || first == 0xdd || first == 0xde || first == 0xdf) {
        return Format::MSGPACK;
    }

    // FlexBuffers: root type is last byte, but we can check for common patterns
    // This is harder to detect reliably; assume if nothing else matches
    // and it's binary, try FlexBuffers

    // Default to MsgPack as it's most common in your stack
    return Format::MSGPACK;
}

}  // namespace zerialize
}  // namespace fivm

#endif  // FIVM_ZERIALIZE_FORMAT_HPP

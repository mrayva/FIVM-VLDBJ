#include <gtest/gtest.h>
#include <vector>
#include <cstdint>

// Include zerialize headers
#include <zerialize/protocols/msgpack.hpp>
#include <zerialize/protocols/cbor.hpp>
#include <zerialize/protocols/flex.hpp>
#include <zerialize/protocols/json.hpp>

// FIVM zerialize adaptor headers
#include "zerialize/queue.hpp"
#include "zerialize/message.hpp"
#include "zerialize/format.hpp"

namespace {

using namespace fivm::zerialize;

// Test basic queue operations
TEST(SPSCQueueTest, PushPop) {
    SPSCQueue<int> queue(16);
    
    EXPECT_TRUE(queue.empty());
    EXPECT_TRUE(queue.try_push(42));
    EXPECT_FALSE(queue.empty());
    
    int value;
    EXPECT_TRUE(queue.try_pop(value));
    EXPECT_EQ(value, 42);
    EXPECT_TRUE(queue.empty());
}

TEST(SPSCQueueTest, FullQueue) {
    SPSCQueue<int> queue(4);  // Capacity will be rounded to 4
    
    EXPECT_TRUE(queue.try_push(1));
    EXPECT_TRUE(queue.try_push(2));
    EXPECT_TRUE(queue.try_push(3));
    // Queue should be full now (capacity-1 = 3 elements for SPSC)
    EXPECT_FALSE(queue.try_push(4));
}

TEST(MPSCQueueTest, PushPop) {
    MPSCQueue<int> queue;
    
    queue.push(1);
    queue.push(2);
    queue.push(3);
    
    int value;
    EXPECT_TRUE(queue.try_pop(value));
    EXPECT_EQ(value, 1);
    EXPECT_TRUE(queue.try_pop(value));
    EXPECT_EQ(value, 2);
    EXPECT_TRUE(queue.try_pop(value));
    EXPECT_EQ(value, 3);
    EXPECT_FALSE(queue.try_pop(value));
}

// Test Message struct
TEST(MessageTest, MoveSemantics) {
    Message msg1{
        {1, 2, 3, 4},
        Format::MSGPACK,
        "TEST_RELATION",
        1
    };
    
    EXPECT_EQ(msg1.data.size(), 4);
    EXPECT_EQ(msg1.format, Format::MSGPACK);
    EXPECT_EQ(msg1.relation, "TEST_RELATION");
    
    Message msg2 = std::move(msg1);
    EXPECT_EQ(msg2.data.size(), 4);
    EXPECT_TRUE(msg1.data.empty());  // Moved from
}

TEST(MessageTest, ViewAccess) {
    Message msg{{0x82, 0xa1, 0x61, 0x01}, Format::MSGPACK, "TEST", 1};
    auto view = msg.view();
    EXPECT_EQ(view.size(), 4);
    EXPECT_EQ(view[0], 0x82);
}

// Test MsgPack serialization
TEST(MsgPackTest, BasicSerialization) {
    zerialize::MsgPack::RootSerializer root;
    zerialize::MsgPack::Serializer ser(root);
    
    ser.begin_map(2);
    ser.key("id");
    ser.int64(42);
    ser.key("name");
    ser.string("test");
    ser.end_map();
    
    auto buf = root.finish();
    EXPECT_GT(buf.size(), 0);
    
    // Deserialize and verify
    zerialize::MsgPack::Deserializer reader(
        std::span<const uint8_t>(buf.data(), buf.size()));
    
    EXPECT_TRUE(reader.isMap());
    EXPECT_EQ(reader["id"].asInt64(), 42);
    EXPECT_EQ(reader["name"].asStringView(), "test");
}

// Test CBOR serialization
TEST(CborTest, BasicSerialization) {
    zerialize::CBOR::RootSerializer root;
    zerialize::CBOR::Serializer ser(root);
    
    ser.begin_map(2);
    ser.key("value");
    ser.double_(3.14159);
    ser.key("flag");
    ser.boolean(true);
    ser.end_map();
    
    auto buf = root.finish();
    EXPECT_GT(buf.size(), 0);
    
    // Deserialize and verify
    zerialize::CBOR::Deserializer reader(
        std::span<const uint8_t>(buf.data(), buf.size()));
    
    EXPECT_TRUE(reader.isMap());
    EXPECT_NEAR(reader["value"].asDouble(), 3.14159, 0.00001);
    EXPECT_TRUE(reader["flag"].asBool());
}

// Test FlexBuffers serialization
TEST(FlexTest, BasicSerialization) {
    zerialize::Flex::RootSerializer root;
    zerialize::Flex::Serializer ser(root);
    
    ser.begin_map(2);
    ser.key("count");
    ser.uint64(100);
    ser.key("label");
    ser.string("hello");
    ser.end_map();
    
    auto buf = root.finish();
    EXPECT_GT(buf.size(), 0);
    
    // Deserialize and verify
    zerialize::Flex::Deserializer reader(
        std::span<const uint8_t>(buf.data(), buf.size()));
    
    EXPECT_TRUE(reader.isMap());
    EXPECT_EQ(reader["count"].asUInt64(), 100);
    EXPECT_EQ(reader["label"].asStringView(), "hello");
}

// Test queue with Messages
TEST(MessageQueueTest, SPSCWithMessages) {
    auto queue = make_message_queue(100);
    
    // Create a MsgPack message
    zerialize::MsgPack::RootSerializer root;
    zerialize::MsgPack::Serializer ser(root);
    ser.begin_map(1);
    ser.key("x");
    ser.int64(123);
    ser.end_map();
    auto buf = root.finish();
    
    Message msg{
        std::vector<uint8_t>(buf.data(), buf.data() + buf.size()),
        Format::MSGPACK,
        "TEST",
        1
    };
    
    EXPECT_TRUE(queue->try_push(std::move(msg)));
    
    Message received;
    EXPECT_TRUE(queue->try_pop(received));
    EXPECT_EQ(received.format, Format::MSGPACK);
    EXPECT_EQ(received.relation, "TEST");
    
    // Verify content
    zerialize::MsgPack::Deserializer reader(received.view());
    EXPECT_EQ(reader["x"].asInt64(), 123);
}

}  // namespace

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

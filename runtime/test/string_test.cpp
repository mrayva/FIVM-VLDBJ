#include <gtest/gtest.h>

#include <string>
#include <thread>
#include <vector>

#include "dbtoaster/string.hpp"

namespace {

using dbtoaster::PooledRefCountedString;

TEST(PooledRefCountedStringTest, BasicConstruction) {
  PooledRefCountedString s("hello");
  EXPECT_EQ(s.size(), 5u);
  EXPECT_STREQ(s.c_str(), "hello");
}

TEST(PooledRefCountedStringTest, CopySharesBuffer) {
  PooledRefCountedString a("shared");
  PooledRefCountedString b(a);
  EXPECT_STREQ(a.c_str(), "shared");
  EXPECT_STREQ(b.c_str(), "shared");
}

TEST(PooledRefCountedStringTest, MoveLeavesSourceEmpty) {
  PooledRefCountedString a("moved");
  PooledRefCountedString b(std::move(a));
  EXPECT_STREQ(b.c_str(), "moved");
  EXPECT_EQ(a.c_str(), std::string(""));
}

TEST(PooledRefCountedStringTest, CopyAssignReleasesOldBuffer) {
  PooledRefCountedString a("first");
  PooledRefCountedString b("second");
  b = a;
  EXPECT_STREQ(a.c_str(), "first");
  EXPECT_STREQ(b.c_str(), "first");
}

TEST(PooledRefCountedStringTest, ReassignFromCString) {
  PooledRefCountedString a("first");
  PooledRefCountedString b = a;  // shares ptr_count_ with a
  a = "second";                  // must not corrupt b's now-independent buffer
  EXPECT_STREQ(a.c_str(), "second");
  EXPECT_STREQ(b.c_str(), "first");
}

// Regression test for a ref-count race (fixed via std::atomic_ref in
// string.hpp): many threads copy-construct and destroy copies of the same
// shared string concurrently. Before the fix, the non-atomic ++/-- on
// *ptr_count_ could lose updates under concurrent access, causing the
// underlying buffer to be freed while still referenced (use-after-free) or
// freed twice (double-free) -- both of which crash or corrupt memory under
// AddressSanitizer/ThreadSanitizer.
TEST(PooledRefCountedStringTest, ConcurrentCopyDestroyIsSafe) {
  constexpr int kThreads = 8;
  constexpr int kIterations = 20000;

  PooledRefCountedString shared("concurrent-payload");

  std::vector<std::thread> threads;
  threads.reserve(kThreads);
  for (int t = 0; t < kThreads; ++t) {
    threads.emplace_back([&shared]() {
      for (int i = 0; i < kIterations; ++i) {
        PooledRefCountedString copy(shared);
        EXPECT_STREQ(copy.c_str(), "concurrent-payload");
      }
    });
  }
  for (auto& th : threads) th.join();

  // The original must still be intact after all concurrent copies dropped.
  EXPECT_STREQ(shared.c_str(), "concurrent-payload");
}

}  // namespace

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

#ifndef FIVM_ZERIALIZE_QUEUE_HPP
#define FIVM_ZERIALIZE_QUEUE_HPP

#include <atomic>
#include <cstddef>
#include <memory>
#include <optional>
#include <vector>

#include "message.hpp"

namespace fivm {
namespace zerialize {

/// Lock-free SPSC (Single Producer Single Consumer) bounded queue.
/// Based on Dmitry Vyukov's bounded SPSC queue algorithm.
/// For MPSC scenarios, use one queue per producer or external synchronization.
template <typename T>
class SPSCQueue {
public:
    explicit SPSCQueue(size_t capacity)
        : capacity_(next_power_of_2(capacity)),
          mask_(capacity_ - 1),
          buffer_(std::make_unique<Slot[]>(capacity_)),
          head_(0),
          tail_(0) {}

    /// Try to push an item. Returns true on success, false if queue is full.
    bool try_push(T&& item) noexcept {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        const size_t next_tail = (tail + 1) & mask_;

        if (next_tail == head_.load(std::memory_order_acquire)) {
            return false;  // Queue is full
        }

        buffer_[tail].value = std::move(item);
        tail_.store(next_tail, std::memory_order_release);
        return true;
    }

    /// Try to pop an item. Returns nullopt if queue is empty.
    std::optional<T> try_pop() noexcept {
        const size_t head = head_.load(std::memory_order_relaxed);

        if (head == tail_.load(std::memory_order_acquire)) {
            return std::nullopt;  // Queue is empty
        }

        T item = std::move(buffer_[head].value);
        head_.store((head + 1) & mask_, std::memory_order_release);
        return item;
    }

    /// Try to pop into provided reference. Returns true on success.
    bool try_pop(T& item) noexcept {
        const size_t head = head_.load(std::memory_order_relaxed);

        if (head == tail_.load(std::memory_order_acquire)) {
            return false;  // Queue is empty
        }

        item = std::move(buffer_[head].value);
        head_.store((head + 1) & mask_, std::memory_order_release);
        return true;
    }

    /// Approximate size (may be stale)
    size_t size_approx() const noexcept {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        const size_t head = head_.load(std::memory_order_relaxed);
        return (tail - head) & mask_;
    }

    /// Check if empty (may be stale)
    bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) ==
               tail_.load(std::memory_order_relaxed);
    }

    /// Capacity of the queue
    size_t capacity() const noexcept { return capacity_; }

private:
    struct Slot {
        T value;
    };

    static size_t next_power_of_2(size_t n) {
        n--;
        n |= n >> 1;
        n |= n >> 2;
        n |= n >> 4;
        n |= n >> 8;
        n |= n >> 16;
        n |= n >> 32;
        return n + 1;
    }

    const size_t capacity_;
    const size_t mask_;
    std::unique_ptr<Slot[]> buffer_;

    // Cache line padding to prevent false sharing
    alignas(64) std::atomic<size_t> head_;
    alignas(64) std::atomic<size_t> tail_;
};

/// Lock-free MPSC (Multiple Producer Single Consumer) queue.
/// Uses a linked list with atomic compare-and-swap for producers.
template <typename T>
class MPSCQueue {
public:
    MPSCQueue() : head_(new Node()), tail_(head_.load()) {}

    ~MPSCQueue() {
        // Drain remaining nodes
        while (Node* node = head_.load()) {
            Node* next = node->next.load();
            delete node;
            if (!next) break;
            head_.store(next);
        }
    }

    /// Push an item (thread-safe for multiple producers)
    void push(T&& item) {
        Node* node = new Node(std::move(item));
        Node* prev = head_.exchange(node, std::memory_order_acq_rel);
        prev->next.store(node, std::memory_order_release);
    }

    /// Try to pop an item (single consumer only)
    std::optional<T> try_pop() {
        Node* tail = tail_;
        Node* next = tail->next.load(std::memory_order_acquire);

        if (!next) {
            return std::nullopt;  // Queue is empty
        }

        tail_ = next;
        T item = std::move(next->value);
        delete tail;
        return item;
    }

    /// Try to pop into provided reference
    bool try_pop(T& item) {
        Node* tail = tail_;
        Node* next = tail->next.load(std::memory_order_acquire);

        if (!next) {
            return false;
        }

        tail_ = next;
        item = std::move(next->value);
        delete tail;
        return true;
    }

    /// Check if empty (may miss concurrent pushes)
    bool empty() const {
        return tail_->next.load(std::memory_order_acquire) == nullptr;
    }

private:
    struct Node {
        T value;
        std::atomic<Node*> next{nullptr};

        Node() = default;
        explicit Node(T&& v) : value(std::move(v)) {}
    };

    alignas(64) std::atomic<Node*> head_;
    alignas(64) Node* tail_;  // Only accessed by consumer
};

/// Type aliases for common use cases
using MessageQueue = SPSCQueue<Message>;
using MessageQueueMPSC = MPSCQueue<Message>;

/// Shared pointer wrappers for easy sharing between threads
using MessageQueuePtr = std::shared_ptr<MessageQueue>;
using MessageQueueMPSCPtr = std::shared_ptr<MessageQueueMPSC>;

/// Factory functions
inline MessageQueuePtr make_message_queue(size_t capacity = 10000) {
    return std::make_shared<MessageQueue>(capacity);
}

inline MessageQueueMPSCPtr make_message_queue_mpsc() {
    return std::make_shared<MessageQueueMPSC>();
}

}  // namespace zerialize
}  // namespace fivm

#endif  // FIVM_ZERIALIZE_QUEUE_HPP

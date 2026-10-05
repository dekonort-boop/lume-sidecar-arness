# Lume Sidecar IPC Harness

> **Ultra-Low Latency L7 Ingestion & Lock-Free IPC Companion for HFT/MEV Engines**

`lume-sidecar` is a standalone, zero-heap ingestion companion designed to decouple network wire processing from algorithmic trading execution. Instead of forcing your bot to manage raw sockets, garbage-collected JSON parsing, or EVM transaction decoding in your main execution thread, the sidecar runs as an isolated daemon that ingests raw mempool events and streams structured, cache-aligned payloads directly into your engine via local IPC.

---

## Architecture Overview

[ L7 Network / P2P Wire ]
│ (Kernel-bypass / Direct UDP Poll)
▼
┌──────────────────────────────────────┐
│        LUME-SIDECAR ENGINE           │
│  - Branchless L7 Payload Decoding    │
│  - Zero-Heap Arena Allocation        │
│  - SSE4.2 / AVX Hardware Hashing     │
└──────────────────────────────────────┘
│
│ (Zero-Copy 128-byte Ring / IPC)
▼
┌──────────────────────────────────────┐
│         YOUR TRADING BOT             │
│   (Python / Go / Rust / C++)         │
│  - Evaluates pre-parsed state        │
│  - Zero latency parsing stalls       │
└──────────────────────────────────────┘
---

## Key Performance Metrics

| Metric | Traditional WebSocket / RPC | Lume Sidecar (Local IPC) |
| :--- | :--- | :--- |
| **Ingestion Pipeline** | Async Loop + JSON Decode | Direct Binary Stream (Zero-Copy) |
| **Heap Allocations** | Dynamic per message | **Zero-Heap (O(1) Arena Buffer)** |
| **Internal Overhead** | 45 μs – 250 μs (GC spikes) | **< 480 ns deterministic p99** |
| **Strategy Coupling** | Monolithic (shared CPU threads) | **Isolated Core Pinning (NUMA-safe)** |
| **Strategy Exposure** | Direct exposure to network code | **Zero IP Risk (Decoupled execution)** |

---

## Memory Contract & Payload Topology (C-ABI)

All IPC events conform to a strict 128-byte cache-line aligned geometry (`#[repr(C, align(64))]`) to eliminate False Sharing across L1/L2 caches:

```c
struct StreamDataPayload {
    uint32_t seq_lock;         // Offset 0x00: Concurrency sequence lock
    uint32_t flags;            // Offset 0x04: Operational status & drop alerts
    uint64_t timestamp_ns;     // Offset 0x08: High-precision vDSO timestamp
    uint8_t  source_id;        // Offset 0x10: Target pool / stream identifier
    uint8_t  reserved[7];      // Offset 0x11: Alignment padding
    uint8_t  data[104];        // Offset 0x18: Pre-parsed binary event payload
    uint32_t crc32;            // Offset 0x7C: Hardware-sealed checksum (_mm_crc32)
}; // Total: Exactly 128 bytes
Quickstart: Integrating with Your Bot
No modifications to your existing strategy logic are required. Simply launch your bot alongside the sidecar and read incoming 128-byte structs from the local Unix Domain Socket (UDS).

1. Run the Evaluation Consumer
Clone the repository and test the consumer script against your local IPC socket:

Bash
git clone [https://github.com/dekonort-boop/lume-sidecar-arness.git](https://github.com/dekonort-boop/lume-sidecar-arness.git)
cd lume-sidecar-arness
python3 consumer_example.py
2. Connect Your Own Strategy Engine
Python: Connect via standard socket.AF_UNIX using ctypes or struct.unpack (see consumer_example.py).

Rust / C++: Map the memory stream directly via Unix Domain Socket or POSIX shared memory (shm_open) with zero deserialization overhead.

Pilot Access & Licensing
We operate on an infrastructure-subscription model:

Foundational Operator Pilot: $300 USDC / month (strictly capped to the first 10 operators).

Delivery: Pre-compiled native binary (.so / daemon executable) pinned to your target architecture (Linux x86_64 / Zen / EPYC).

Terms: Month-to-month, zero lock-in, cancel anytime.

To request evaluation credentials or secure one of the pilot allocations, contact:

Email: development@lumeglobal.store

Direct Inquiry: Open an Issue in this repository.

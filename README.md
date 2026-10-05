# Lume Sidecar IPC Harness

> **Ultra-Low Latency L7 Ingestion & Lock-Free IPC Companion for HFT/MEV Engines**

`lume-sidecar` is a standalone, zero-heap ingestion companion designed to decouple network wire processing from algorithmic trading execution. Instead of forcing your bot to manage raw sockets, garbage-collected JSON parsing, or EVM transaction decoding in your main execution thread, the sidecar runs as an isolated daemon that ingests raw mempool events and streams structured, cache-aligned payloads directly into your engine via local IPC.

---

## Architecture Overview

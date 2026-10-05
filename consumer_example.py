#!/usr/bin/env python3
"""
Lume Sidecar IPC - Minimal Python Consumer Example
Reads deterministic 128-byte binary payloads from the sidecar IPC stream.
"""

import socket
import struct
import os
import sys

IPC_SOCKET_PATH = "/tmp/lume_sidecar.sock"
PAYLOAD_SIZE = 128
HEADER_FORMAT = "<IIQB7s"
HEADER_SIZE = 24  # seq_lock (4) + flags (4) + timestamp (8) + source_id (1) + pad (7)

def run_consumer(sock_path: str):
    if not os.path.exists(sock_path):
        print(f"[!] IPC Socket not found at {sock_path}")
        print("[*] Launch the lume-sidecar daemon first, or verify socket permissions.")
        return

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(sock_path)
        print(f"[*] Connected to Lume Sidecar on {sock_path}")
        print("[*] Listening for cache-aligned 128-byte events...\n")

        while True:
            raw_buffer = bytearray()
            while len(raw_buffer) < PAYLOAD_SIZE:
                chunk = client.recv(PAYLOAD_SIZE - len(raw_buffer))
                if not chunk:
                    print("[!] Stream closed by sidecar.")
                    return
                raw_buffer.extend(chunk)

            # Parse 128-byte payload
            seq_lock, flags, ts_ns, source_id, _ = struct.unpack(
                HEADER_FORMAT, raw_buffer[:HEADER_SIZE]
            )
            event_body = raw_buffer[HEADER_SIZE:124]
            crc32_val = struct.unpack("<I", raw_buffer[124:128])[0]

            # Yield to trading logic
            print(
                f"[IPC EVENT] Seq: {seq_lock} | Source: {source_id} | "
                f"Latency TS: {ts_ns} ns | Flags: {hex(flags)} | CRC32: {hex(crc32_val)}"
            )

    except KeyboardInterrupt:
        print("\n[*] Consumer terminated by operator.")
    finally:
        client.close()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else IPC_SOCKET_PATH
    run_consumer(path)

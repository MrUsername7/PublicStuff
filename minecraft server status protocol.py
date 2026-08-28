import socket
import struct
import json
import time


HOST = "138.88.170.113"
PORT = 23309
PROTOCOL = 774  # 1.21.6


# -----------------------------
# VarInt
# -----------------------------

def write_varint(value):
    out = bytearray()

    while True:
        b = value & 0x7F
        value >>= 7

        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            break

    return bytes(out)


def read_varint(sock):
    value = 0
    position = 0

    while True:
        b = sock.recv(1)

        if not b:
            raise ConnectionError("Connection closed")

        b = b[0]

        value |= (b & 0x7F) << position

        if not (b & 0x80):
            break

        position += 7

        if position > 35:
            raise ValueError("Invalid VarInt")

    return value


def read_varint_bytes(data, index):
    value = 0
    position = 0

    while True:
        b = data[index]
        index += 1

        value |= (b & 0x7F) << position

        if not (b & 0x80):
            break

        position += 7

    return value, index


def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        part = sock.recv(size - len(data))

        if not part:
            raise ConnectionError("Connection closed")

        data += part

    return data


# -----------------------------
# Connect
# -----------------------------

print(f"Connecting to {HOST}:{PORT}...")

sock = socket.create_connection((HOST, PORT))

print("Connected.\n")


# -----------------------------
# Handshake
# -----------------------------

packet = bytearray()

packet += write_varint(0)
packet += write_varint(PROTOCOL)

host = HOST.encode("utf8")
packet += write_varint(len(host))
packet += host

packet += struct.pack(">H", PORT)

packet += write_varint(1)

full = write_varint(len(packet)) + packet

print("=== HANDSHAKE ===")
print("Packet Length :", len(packet))
print("Protocol      :", PROTOCOL)
print("Host          :", HOST)
print("Port          :", PORT)
print("State         : STATUS")
print("Bytes Sent    :", full.hex())
print()

sock.sendall(full)


# -----------------------------
# Status Request
# -----------------------------

request = write_varint(1) + write_varint(0)

print("=== STATUS REQUEST ===")
print("Bytes Sent :", request.hex())
print()

sock.sendall(request)


# -----------------------------
# Receive Status
# -----------------------------

packet_length = read_varint(sock)
packet = recv_exact(sock, packet_length)

print("=== STATUS RESPONSE ===")
print("Packet Length :", packet_length)
print("Raw Packet:")
print(packet.hex())
print()

index = 0

packet_id, index = read_varint_bytes(packet, index)
json_length, index = read_varint_bytes(packet, index)

json_text = packet[index:index + json_length].decode("utf8")

print("Packet ID   :", packet_id)
print("JSON Length :", json_length)
print()

print("JSON:")
print(json.dumps(json.loads(json_text), indent=4))
print()

status = json.loads(json_text)


# -----------------------------
# Pretty Print
# -----------------------------

print("=========== SERVER INFO ===========")

version = status.get("version", {})
players = status.get("players", {})
description = status.get("description", {})

print("Version :", version.get("name"))
print("Protocol:", version.get("protocol"))

print()

print("Players :", players.get("online"), "/", players.get("max"))

print()

if isinstance(description, dict):

    if "extra" in description:
        motd = "".join(
            part.get("text", "")
            for part in description["extra"]
        )
    else:
        motd = description.get("text", "")

else:
    motd = str(description)

print("MOTD:")
print(motd)

print()

print("Favicon :", "Yes" if "favicon" in status else "No")
print("Secure Chat :", status.get("enforcesSecureChat"))

print()


# -----------------------------
# Ping
# -----------------------------

print("=== PING ===")

payload = int(time.time() * 1000)

ping = (
    write_varint(9)
    + write_varint(1)
    + struct.pack(">Q", payload)
)

start = time.perf_counter()

sock.sendall(ping)

length = read_varint(sock)
pong = recv_exact(sock, length)

end = time.perf_counter()

print("Raw Pong:")
print(pong.hex())

index = 0

packet_id, index = read_varint_bytes(pong, index)

returned = struct.unpack(">Q", pong[index:index + 8])[0]

print()

print("Packet ID :", packet_id)
print("Returned Payload :", returned)
print("Latency : %.2f ms" % ((end - start) * 1000))

sock.close()

print("\nDone.")

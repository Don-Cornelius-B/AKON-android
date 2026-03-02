# AKON
### Encrypted Peer-to-Peer LoRa Communication System

> Secure, off-grid, long-range messaging — no internet required.

---

## Overview

AKON is a secure peer-to-peer communication system built for experimental, disaster-response, and off-grid use cases. It bridges two ESP32 + LoRa nodes over long-range RF, with a Python/Kivy mobile application serving as the user interface. Messages are AES-128 encrypted at the firmware level before transmission — no cloud, no infrastructure, no compromise.

---

## Problem Statement

Modern communication relies entirely on centralised infrastructure. When that infrastructure fails — natural disasters, remote deployments, network outages — so does communication. AKON solves this by enabling direct, encrypted, long-range radio messaging between two parties using commodity hardware and an open-source software stack.

---

## System Architecture

```
┌──────────┐      WiFi (SoftAP)     ┌──────────────┐
│  Phone   │ ◄──────────────────── │    ESP32 A   │
│ (Kivy)   │ ──────────────────► │  + SX127x LoRa│
└──────────┘                        └──────┬───────┘
                                           │
                                    Long-Range RF
                                   (433/868/915 MHz)
                                           │
                                    ┌──────┴───────┐      WiFi (SoftAP)     ┌──────────┐
                                    │    ESP32 B   │ ──────────────────► │  Phone   │
                                    │  + SX127x LoRa│ ◄────────────────── │ (Kivy)   │
                                    └──────────────┘                        └──────────┘
```

```
Phone → [ESP32 → LoRa] )))) Long Range RF (((( [LoRa → ESP32] → Phone
```

---

## Communication Flow

1. The user types a message in the Kivy mobile application.
2. The phone connects to the ESP32 over its local WiFi (SoftAP mode) — no internet involved.
3. The message is sent via UDP broadcast to the ESP32 on port `5000`.
4. The ESP32 **encrypts** the message payload using **AES-128** before placing it on the LoRa radio.
5. The LoRa module transmits the encrypted packet over long-range RF (433 / 868 / 915 MHz).
6. The receiving ESP32 picks up the RF packet, **decrypts** it, and forwards the plaintext to the connected phone over its local WiFi.
7. The Kivy app renders the incoming message as a chat bubble in real time.

---

## Packet Structure

| Field      | Size     | Description                          |
|------------|----------|--------------------------------------|
| Node ID    | Variable | Sender identifier (e.g. `Node_A`)    |
| Separator  | 1 byte   | `:` delimiter                        |
| Payload    | Variable | Message content (AES-128 encrypted on LoRa link) |

On the UDP layer, the full packet is UTF-8 encoded with a maximum buffer size of **1024 bytes**.

---

## Encryption Architecture

- **Algorithm:** AES-128 (symmetric block cipher)
- **Where:** Implemented in ESP32 Arduino firmware
- **Scope:** Only the LoRa RF link is encrypted; local WiFi traffic is LAN-only and never leaves the device's SoftAP network
- **Key Management:** Pre-shared key (PSK) — both ESP32 nodes must be flashed with the same key
- **Future:** Diffie-Hellman or ECDH key exchange is planned (see Roadmap)

---

## Hardware Components

| Component              | Purpose                                      |
|------------------------|----------------------------------------------|
| ESP32 (×2)             | Main microcontroller — WiFi SoftAP + LoRa SPI|
| SX1276 / SX1278 (×2)  | LoRa transceiver module (long-range RF)      |
| Android phone (×2)     | Runs the Kivy application                    |
| USB-C / Micro USB cable| Firmware flashing                            |
| 3.3V power supply      | Powers the ESP32 + LoRa module               |

---

## Software Stack

| Layer         | Technology                        |
|---------------|-----------------------------------|
| Mobile UI     | Python 3, Kivy                    |
| Android Build | Buildozer                         |
| Networking    | UDP broadcast (LAN only)          |
| Firmware      | Arduino framework (C++) on ESP32  |
| RF Transport  | LoRa via SX1276/SX1278            |
| Encryption    | AES-128 (ESP32 firmware)          |

---

## Installation & Setup

### Prerequisites

- Python 3.8+ (minimum tested version; required for f-string and `walrus` compatibility in dependencies)
- pip
- (For Android build) Linux/macOS, OpenJDK 17 (recommended), Android SDK/NDK

---

### 1. Python / Kivy Environment

```bash
# Clone the repository
git clone https://github.com/Don-Cornelius-B/AKON-android.git
cd AKON-android

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install kivy
```

Run the app on desktop for testing:

```bash
python main.py
```

---

### 2. Build Android APK (Buildozer)

```bash
# Install Buildozer
pip install buildozer

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y \
    python3-pip build-essential git ffmpeg libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev \
    libavformat-dev libavcodec-dev zlib1g-dev openjdk-17-jdk

# Build debug APK
buildozer android debug

# Deploy to connected device
buildozer android deploy run
```

The compiled APK will be in the `bin/` directory.

---

### 3. ESP32 Firmware Flashing

1. Open the `firmware/` directory in the Arduino IDE or PlatformIO.
2. Install the required libraries:
   - `LoRa` by Sandeep Mistry
   - `AESLib` or equivalent AES-128 library
3. Set the pre-shared AES key in `firmware/config.h`:

```cpp
#define AES_KEY "0123456789ABCDEF"   // Must be exactly 16 characters
```

4. Select board: **ESP32 Dev Module**
5. Flash to both ESP32 nodes:

```bash
# Using esptool (alternative to Arduino IDE)
esptool.py --port /dev/ttyUSB0 write_flash 0x0 firmware.bin
```

---

### 4. LoRa Configuration Parameters

Configure these in the ESP32 firmware to match on **both** nodes:

| Parameter    | Default Value | Notes                          |
|--------------|---------------|--------------------------------|
| Frequency    | 433 MHz       | Change to 868/915 for your region |
| Bandwidth    | 125 kHz       |                                |
| Spread Factor| SF7           | Higher SF = longer range, slower |
| Coding Rate  | 4/5           |                                |
| TX Power     | 17 dBm        | Max 20 dBm for SX1276          |
| Sync Word    | `0x12`        | Private network byte           |

---

## Usage

1. Power on both ESP32 nodes.
2. On each phone, connect to the ESP32's WiFi network (SSID defined in firmware, e.g. `AKON_NODE_A`).
3. Launch the AKON app.
4. Enter a **Node Name** on the identity screen and tap **INITIALIZE GATEWAY**.
5. Type a message in the input field and tap **SHOUT** to send.
6. Incoming messages appear automatically as chat bubbles.

---

## Project Structure

```
AKON-android/
├── main.py           # Kivy application — UI layout and app logic
├── network.py        # UDP networking layer (send/receive over WiFi LAN)
├── config.py         # Centralised configuration (ports, colours, addresses)
├── buildozer.spec    # Android build configuration
└── firmware/         # ESP32 Arduino firmware (LoRa + AES-128)
    ├── akon_node.ino
    └── config.h
```

---

## Roadmap

- [x] Kivy chat UI (login + chat screens)
- [x] UDP broadcast networking over ESP32 SoftAP WiFi
- [x] AES-128 encryption on LoRa link (firmware)
- [ ] Firmware source code added to repository
- [ ] Persistent message history (SQLite)
- [ ] Node discovery / presence indicators
- [ ] Message acknowledgement and delivery receipts
- [ ] LoRa mesh networking (multi-hop relay)
- [ ] ECDH / Diffie-Hellman key exchange (replace PSK)
- [ ] OTA (Over-the-Air) firmware updates for ESP32
- [ ] iOS support via Kivy/Buildozer

---

## Future Scope

| Feature                    | Description                                                         |
|----------------------------|---------------------------------------------------------------------|
| **Mesh Networking**        | Multi-hop LoRa relay enabling larger coverage areas                 |
| **Secure Key Exchange**    | ECDH handshake to eliminate the need for a pre-shared key           |
| **OTA Updates**            | Remote firmware updates for deployed ESP32 nodes                    |
| **Group Messaging**        | Broadcast to multiple nodes simultaneously                          |
| **GPS Integration**        | Attach location data to messages for disaster-response mapping      |
| **Repeater Mode**          | Dedicated relay nodes to extend network range without a phone       |
| **Message Signing**        | ECDSA signatures to verify message authenticity                     |

---

## Contributing

Contributions are welcome. To get started:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: describe your change"`
4. Push to your fork: `git push origin feature/your-feature`
5. Open a Pull Request against `main`.

Please keep commits focused and write clear PR descriptions. For significant changes, open an issue first to discuss the approach.

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

> AKON is an experimental project. Use responsibly and in compliance with local RF transmission regulations.

# Metro Digitale - Complete Firmware Architecture

## Overview

This document describes the complete firmware architecture for the Metro Digitale ESP32-S3 based digital measurement tool.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   UI     │  │  Config  │  │  Modes   │  │  Logic   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                   Core Subsystems Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Puntali  │  │Measurement│  │  BLE     │  │ Feedback │   │
│  │ Database │  │Calculator │  │ Multi-   │  │  System  │   │
│  │          │  │  Sender   │  │ Device   │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                    Hardware Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   GPIO   │  │  AS5600  │  │ SD Card  │  │  LEDC    │   │
│  │  Button  │  │ Encoder  │  │  FATFS   │  │  Buzzer  │   │
│  │   LED    │  │   I2C    │  │   SPI    │  │   PWM    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### Hardware Layer

#### hardware_gpio.c/.h
- **Physical SEND button** (GPIO 25) with debouncing and interrupt handling
- **Status LED** (GPIO 27) for visual feedback
- **Buzzer** (GPIO 14) using LEDC PWM for tone generation
- Button callback system for event-driven architecture

#### encoder_reader.c/.h
- **AS5600 magnetic encoder** interface over I2C
- 12-bit resolution (4096 positions per revolution)
- Magnet detection and validation
- AGC and magnitude reading for diagnostics
- Angle to linear position conversion

#### sd_card.c/.h
- **SD card** mounting via SPI interface
- FAT filesystem support
- Directory structure management (`/puntali`, `/config`, `/cache`)
- File operations (read, write, delete, list)
- Automatic creation of standard directories

### Puntali (Tip Management) Layer

#### puntale_types.h/.c
- **Tip data structures** and enums
- **PuntaleShape**: FLAT, CIRCULAR, CONICAL, CUSTOM
- **PuntaleReference**: EXTERNAL, INTERNAL, CENTER
- **STL model** representation with triangles and vertices
- Correction calculation based on reference type

#### stl_parser.h/.c
- **STL binary file parser**
- Triangle extraction from STL format
- Bounding box calculation
- Model normalization for display
- Memory-efficient streaming parser

#### puntale_database.h/.c
- **In-memory tip database** (up to 32 tips)
- **SD card scanning** for STL files
- **NVS persistence** for tip configurations
- Lazy STL loading (load only when needed)
- Tip CRUD operations (Create, Read, Update, Delete)

### Measurement Layer

#### measure_calculator.h/.c
- **Universal measurement formula**:
  ```
  Net = (Encoder + RangeOffsetL + RangeOffsetR + CorrL + CorrR) × Factor + AddOffset
  ```
- **Hybrid tip support** (different reference types per tip)
- **Correction calculation**:
  - EXTERNAL: subtract thickness
  - INTERNAL: add diameter
  - CENTER: no correction
- Human-readable formula generation

#### mode_device_routing.h/.c
- **Mode-to-device mapping** configuration
- **Device types**: BLITZ, SMARTPHONE, PC, CUSTOM
- **Blitz operation modes**: semi_auto, automatico
- **NVS persistence** for routing configuration
- Broadcast mode support (send to all devices)

#### measure_sender.h/.c
- **BLE transmission** with automatic routing
- **JSON payload generation** with all measurement data
- **Device-specific sending** or broadcast
- Integration with multi-device BLE system

### BLE (Bluetooth Low Energy) Layer

#### ble_server.h/.c
- **GATT server** implementation
- **Service UUID**: `12345678-1234-1234-1234-123456789abc`
- **Characteristics**:
  - TX (Metro → Device): `...789abd`
  - RX (Device → Metro): `...789abe`
- **Advertising** management
- **Multi-connection support** (up to 3 devices)

#### ble_multi_device.h/.c
- **Device database** with 3 simultaneous connections
- **Device identification protocol** (handshake)
- **Connection state management**
- **Routing table** (connection ID ↔ device ID)
- **NVS persistence** for known devices
- **Feedback integration** (buzzer/LED on connect/disconnect)

### Feedback Layer

#### buzzer_feedback.h/.c
- **Musical tone sequences** for events:
  - Success: C5-E5-G5 ascending (~310ms)
  - Error: C5-C5-C5 trill (~400ms)
  - Mode change: D5-A5 double note (~250ms)
  - Button press: C6 short click (~30ms)
  - BT connected: C5-D5-E5-G5 scale (~500ms)
  - BT disconnected: G5-E5-C5 descending (~400ms)

#### led_feedback.h/.c
- **LED patterns**:
  - Success: 3× blink
  - Error: 5× fast blink
  - Button press: 1× short blink
  - BT connected: Steady on
  - BT disconnected: Off
  - Working: Slow pulse

## Data Flow

### Measurement Workflow

```
┌─────────────┐
│ SEND Button │
│   Pressed   │
└──────┬──────┘
       ↓
┌──────────────────┐
│ Read Encoder     │
│ Position (AS5600)│
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Get Active Tips  │
│ (Left & Right)   │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Calculate Net    │
│ Measurement      │
│ (Universal Formula)
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Get Mode Routing │
│ Configuration    │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Generate JSON    │
│ Payload          │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Send via BLE     │
│ to Target Device │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Play Success/    │
│ Error Feedback   │
└──────────────────┘
```

### BLE Connection Workflow

```
┌─────────────┐
│ Device      │
│ Connects    │
└──────┬──────┘
       ↓
┌──────────────────┐
│ Assign Device ID │
│ (0, 1, or 2)     │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Wait for         │
│ Identification   │
│ Message          │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Parse JSON:      │
│ {"command":      │
│  "identify",     │
│  "device_type":  │
│  "blitz"}        │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Set Device Type  │
│ & Name           │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Send Ack:        │
│ {"status":       │
│  "identified"}   │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Save to NVS      │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Play Connected   │
│ Feedback         │
└──────────────────┘
```

## Memory Management

### Static Allocations
- **Tip database**: 32 × ~2KB = ~64KB
- **Device database**: 3 × ~100B = ~300B
- **BLE buffers**: ~4KB per connection = ~12KB
- **STL models**: Loaded on-demand, max 1-2 active

### Dynamic Allocations
- **STL triangles**: malloc() per model
- **File buffers**: Temporary, freed after use
- **JSON buffers**: Stack-allocated, 1KB typical

### PSRAM Usage
- **Large STL models** (> 100KB)
- **Display framebuffers** (if using LVGL)
- **Cached thumbnails**

## Configuration Storage (NVS)

### Namespaces

1. **"puntali"** - Tip configurations
   ```
   <tip_id>_shape:      uint8 (PuntaleShape)
   <tip_id>_thick:      uint32 (float bits)
   <tip_id>_ref:        uint8 (PuntaleReference)
   <tip_id>_offset:     uint32 (float bits)
   <tip_id>_name:       string
   ```

2. **"mode_routing"** - Mode-to-device routing
   ```
   route_fermavetro:    uint8 (packed: type + device_id)
   route_vetri:         uint8
   route_astine:        uint8
   route_calibro:       uint8
   route_rilievi:       uint8
   ```

3. **"devices"** - Known BLE devices
   ```
   dev<n>_type:         uint8 (DeviceType)
   dev<n>_name:         string
   dev<n>_mac:          string
   ```

4. **"ui_settings"** - UI preferences
   ```
   blitz_mode:          uint8 (BlitzMode)
   buzzer_volume:       uint8
   led_brightness:      uint8
   auto_reconnect:      uint8
   ```

## Build Configuration

### ESP-IDF Components
- `nvs_flash` - Non-volatile storage
- `bt` - Bluetooth stack
- `driver` - GPIO, I2C, SPI, LEDC
- `esp_timer` - Timing utilities
- `lvgl` - UI graphics (when UI implemented)
- `fatfs` - FAT filesystem for SD card
- `spi_flash` - Flash memory operations

### sdkconfig Highlights
- **Target**: ESP32-S3
- **Flash**: 8MB
- **PSRAM**: 8MB OPI @ 80MHz
- **Bluetooth**: BLE 5.0 only
- **CPU**: Dual-core @ 240MHz
- **Partition**: Single app (large)

## Error Handling

### Critical Errors (System Halt)
- NVS initialization failure
- Mutex creation failure
- Memory allocation failure (out of RAM)

### Recoverable Errors (Log & Continue)
- SD card not present
- AS5600 encoder not detected (fallback to alternate)
- BLE connection lost (auto-reconnect)
- STL file parsing error (skip file)

### User Feedback
- **Buzzer tones** for immediate feedback
- **LED patterns** for visual status
- **Log messages** via UART (for debugging)

## Performance Characteristics

### Timing
- **Button response**: < 50ms (debounced)
- **Measurement calculation**: < 5ms
- **BLE transmission**: < 100ms
- **Encoder reading**: 100Hz (10ms)
- **Main loop**: 10Hz (100ms)

### Throughput
- **Measurements/second**: ~10 (button-limited)
- **BLE data rate**: ~1KB/s per device
- **SD card read**: ~500KB/s (SPI mode)

## Testing Strategy

### Unit Tests
- STL parser with known binary files
- Measurement calculator with test cases
- Tip correction formulas
- JSON serialization/deserialization

### Integration Tests
- BLE connection with simulated devices
- Measurement workflow end-to-end
- SD card file operations
- NVS persistence across reboots

### Hardware Tests
- Button press and debouncing
- LED patterns visual verification
- Buzzer tones audio verification
- Encoder accuracy and linearity

## Security Considerations

- **No authentication** on BLE (open connections)
- **No encryption** on NVS (consider enabling for production)
- **No signature verification** on STL files
- **Input validation** on received JSON data
- **Buffer overflow protection** via size checks

## Future Enhancements

1. **WiFi OTA updates**
2. **Cloud backup** of configurations
3. **Multi-language** UI support
4. **Advanced analytics** (measurement statistics)
5. **Predictive maintenance** (encoder health monitoring)
6. **Mobile app** deep integration
7. **Voice feedback** for accessibility
8. **Barcode scanning** for tip identification

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-18  
**Author**: Metro Digitale Firmware Team

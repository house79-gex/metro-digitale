#ifndef MODE_DEVICE_ROUTING_H
#define MODE_DEVICE_ROUTING_H

#include "measure_calculator.h"
#include "esp_err.h"
#include <stdint.h>

// Device types
typedef enum {
    DEVICE_TYPE_NONE = 0,
    DEVICE_TYPE_BLITZ,          // CNC saw (Raspberry Pi)
    DEVICE_TYPE_SMARTPHONE,     // Android app
    DEVICE_TYPE_PC,             // Generic PC
    DEVICE_TYPE_CUSTOM          // Custom device
} DeviceType;

// Blitz operation mode
typedef enum {
    BLITZ_MODE_SEMI_AUTO = 0,   // Semi-automatic
    BLITZ_MODE_AUTOMATICO       // Automatic batch mode
} BlitzMode;

// Device information
typedef struct {
    uint8_t device_id;                  // Assigned ID (0-2)
    char device_name[48];               // Device name
    char mac_address[18];               // MAC address (XX:XX:XX:XX:XX:XX)
    DeviceType device_type;             // Device type
    bool is_connected;                  // Connection status
    uint32_t last_activity_timestamp;   // Last activity time
    char version[16];                   // Device software version
} DeviceInfo;

// Routing configuration
typedef struct {
    MeasureMode mode;
    DeviceType target_device_type;      // Target device type for this mode
    uint8_t target_device_id;           // Specific device ID (255 = broadcast to all)
    bool broadcast_to_all;              // Send to all connected devices
} RoutingConfig;

// Initialize routing system
esp_err_t mode_device_routing_init(void);

// Set routing for a mode
esp_err_t mode_device_routing_set(MeasureMode mode, DeviceType device_type, uint8_t device_id);

// Get routing for a mode
esp_err_t mode_device_routing_get(MeasureMode mode, DeviceType *device_type, uint8_t *device_id);

// Enable/disable broadcast mode for a mode
esp_err_t mode_device_routing_set_broadcast(MeasureMode mode, bool broadcast);

// Get broadcast setting for a mode
bool mode_device_routing_is_broadcast(MeasureMode mode);

// Save routing configuration to NVS
esp_err_t mode_device_routing_save_to_nvs(void);

// Load routing configuration from NVS
esp_err_t mode_device_routing_load_from_nvs(void);

// Get mode name as string
const char* mode_device_routing_get_mode_name(MeasureMode mode);

// Get device type name as string
const char* mode_device_routing_get_device_type_name(DeviceType type);

// Blitz mode management
esp_err_t mode_device_routing_set_blitz_mode(BlitzMode mode);
BlitzMode mode_device_routing_get_blitz_mode(void);
const char* mode_device_routing_get_blitz_mode_name(BlitzMode mode);

#endif // MODE_DEVICE_ROUTING_H

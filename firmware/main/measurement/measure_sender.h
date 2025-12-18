#ifndef MEASURE_SENDER_H
#define MEASURE_SENDER_H

#include "measure_calculator.h"
#include "mode_device_routing.h"
#include "esp_err.h"

// Send measurement via BLE with automatic routing
esp_err_t measure_sender_send(MeasureMode mode, 
                               const MeasurementResult *result,
                               const Puntale *tip_left,
                               const Puntale *tip_right);

// Send to specific device by ID
esp_err_t measure_sender_send_to_device(uint8_t device_id,
                                        MeasureMode mode,
                                        const MeasurementResult *result,
                                        const Puntale *tip_left,
                                        const Puntale *tip_right);

// Broadcast to all connected devices
esp_err_t measure_sender_broadcast(MeasureMode mode,
                                   const MeasurementResult *result,
                                   const Puntale *tip_left,
                                   const Puntale *tip_right);

// Generate JSON payload for transmission
esp_err_t measure_sender_create_json(MeasureMode mode,
                                     const MeasurementResult *result,
                                     const Puntale *tip_left,
                                     const Puntale *tip_right,
                                     char *json_buffer,
                                     size_t buffer_size);

#endif // MEASURE_SENDER_H

#ifndef ENCODER_H
#define ENCODER_H

#include <stdint.h>
#include "config.h"

// Pin per encoder (da configurare secondo hardware)
#define ENCODER_PIN_A    GPIO_NUM_4
#define ENCODER_PIN_B    GPIO_NUM_5
#define ENCODER_PCNT_UNIT  PCNT_UNIT_0

// Inizializzazione encoder
esp_err_t encoder_init(void);

// Lettura posizione encoder
int32_t encoder_get_count(void);
float encoder_get_position_mm(void);

// Reset/Zero
void encoder_zero(void);
void encoder_set_zero_position(float position_mm);

// Calcoli per modalità specifiche
float encoder_calc_fermavetro_netto(const GlobalConfig *cfg);
float encoder_calc_vetro_netto(const GlobalConfig *cfg, float raw_mm);
float encoder_calc_astina_taglio(const GlobalConfig *cfg, float raw_mm);

// Task encoder (da eseguire su Core 1)
void encoder_task(void *pvParameters);

#endif // ENCODER_H

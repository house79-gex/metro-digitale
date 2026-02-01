#ifndef UI_TOAST_H
#define UI_TOAST_H

#include <stdint.h>

/**
 * @file ui_toast.h
 * @brief Toast notifications per feedback utente
 * 
 * Notifiche temporanee non-blocking con auto-delete.
 */

/**
 * @brief Mostra toast notification
 * 
 * Posizione: bottom-center, sopra nav bar
 * Durata: 2 secondi
 * Stile: background scuro, border verde, padding 15px
 * 
 * @param message Messaggio da mostrare (max 100 caratteri)
 */
void ui_show_toast(const char *message);

/**
 * @brief Mostra toast con durata personalizzata
 * 
 * @param message Messaggio da mostrare
 * @param duration_ms Durata in millisecondi
 */
void ui_show_toast_duration(const char *message, uint32_t duration_ms);

/**
 * @brief Mostra toast di successo (icona ✓, colore verde)
 * 
 * @param message Messaggio da mostrare
 */
void ui_show_toast_success(const char *message);

/**
 * @brief Mostra toast di errore (icona ✗, colore rosso)
 * 
 * @param message Messaggio da mostrare
 */
void ui_show_toast_error(const char *message);

/**
 * @brief Mostra toast di warning (icona ⚠, colore arancio)
 * 
 * @param message Messaggio da mostrare
 */
void ui_show_toast_warning(const char *message);

#endif // UI_TOAST_H

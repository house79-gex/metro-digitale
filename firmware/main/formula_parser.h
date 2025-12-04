#ifndef FORMULA_PARSER_H
#define FORMULA_PARSER_H

#include <stdbool.h>
#include "config.h"

// Tipi di token
typedef enum {
    TOKEN_NUMBER,
    TOKEN_VARIABLE,
    TOKEN_OPERATOR,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_END,
    TOKEN_ERROR
} TokenType;

// Token
typedef struct {
    TokenType type;
    float value;
    char op;
    char var_name[16];
} Token;

// Risultato parsing
typedef struct {
    bool success;
    float value;
    char error_message[128];
} ParseResult;

/**
 * @brief Valuta una formula matematica con variabili
 * 
 * @param formula Stringa formula (es: "(L+6)/2")
 * @param variabili Array di variabili disponibili
 * @param num_variabili Numero di variabili
 * @return ParseResult Risultato con success, value ed eventuali errori
 */
ParseResult formula_parser_evaluate(const char *formula, 
                                     const VariabileRilievo *variabili,
                                     uint8_t num_variabili);

/**
 * @brief Valida una formula senza calcolarla
 * 
 * @param formula Stringa formula da validare
 * @return true se la formula è sintatticamente corretta
 */
bool formula_parser_validate(const char *formula);

/**
 * @brief Ottiene il valore di una variabile per nome
 * 
 * @param nome Nome variabile (es: "L", "H")
 * @param variabili Array variabili
 * @param num_variabili Numero variabili
 * @param out_value Puntatore per output valore
 * @return true se variabile trovata
 */
bool formula_parser_get_variable(const char *nome,
                                 const VariabileRilievo *variabili,
                                 uint8_t num_variabili,
                                 float *out_value);

#endif // FORMULA_PARSER_H

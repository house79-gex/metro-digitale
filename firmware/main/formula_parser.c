#include "formula_parser.h"
#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include "esp_log.h"

static const char *TAG = "FORMULA_PARSER";

// Parser context
typedef struct {
    const char *input;
    size_t pos;
    Token current_token;
    const VariabileRilievo *variabili;
    uint8_t num_variabili;
    char error[128];
} ParserContext;

// Forward declarations
static float parse_expression(ParserContext *ctx);
static float parse_term(ParserContext *ctx);
static float parse_factor(ParserContext *ctx);
static void next_token(ParserContext *ctx);

// Inizializza parser context
static void init_parser(ParserContext *ctx, const char *formula,
                       const VariabileRilievo *vars, uint8_t num_vars) {
    ctx->input = formula;
    ctx->pos = 0;
    ctx->variabili = vars;
    ctx->num_variabili = num_vars;
    ctx->error[0] = '\0';
    next_token(ctx);
}

// Skip whitespace
static void skip_whitespace(ParserContext *ctx) {
    while (ctx->input[ctx->pos] && isspace(ctx->input[ctx->pos])) {
        ctx->pos++;
    }
}

// Get next token
static void next_token(ParserContext *ctx) {
    skip_whitespace(ctx);
    
    if (!ctx->input[ctx->pos]) {
        ctx->current_token.type = TOKEN_END;
        return;
    }
    
    char ch = ctx->input[ctx->pos];
    
    // Numbers
    if (isdigit(ch) || ch == '.') {
        char num_str[32];
        size_t i = 0;
        bool has_dot = false;
        
        while ((isdigit(ctx->input[ctx->pos]) || ctx->input[ctx->pos] == '.') 
               && i < sizeof(num_str) - 1) {
            if (ctx->input[ctx->pos] == '.') {
                if (has_dot) {
                    snprintf(ctx->error, sizeof(ctx->error), "Invalid number format");
                    ctx->current_token.type = TOKEN_ERROR;
                    return;
                }
                has_dot = true;
            }
            num_str[i++] = ctx->input[ctx->pos++];
        }
        num_str[i] = '\0';
        
        ctx->current_token.type = TOKEN_NUMBER;
        ctx->current_token.value = atof(num_str);
        return;
    }
    
    // Variables (uppercase letters)
    if (isupper(ch)) {
        size_t i = 0;
        while (isupper(ctx->input[ctx->pos]) && i < sizeof(ctx->current_token.var_name) - 1) {
            ctx->current_token.var_name[i++] = ctx->input[ctx->pos++];
        }
        ctx->current_token.var_name[i] = '\0';
        ctx->current_token.type = TOKEN_VARIABLE;
        return;
    }
    
    // Operators
    if (ch == '+' || ch == '-' || ch == '*' || ch == '/') {
        ctx->current_token.type = TOKEN_OPERATOR;
        ctx->current_token.op = ch;
        ctx->pos++;
        return;
    }
    
    // Parentheses
    if (ch == '(') {
        ctx->current_token.type = TOKEN_LPAREN;
        ctx->pos++;
        return;
    }
    
    if (ch == ')') {
        ctx->current_token.type = TOKEN_RPAREN;
        ctx->pos++;
        return;
    }
    
    // Unknown character
    snprintf(ctx->error, sizeof(ctx->error), "Unexpected character: %c", ch);
    ctx->current_token.type = TOKEN_ERROR;
}

// Parse factor: number | variable | (expression)
static float parse_factor(ParserContext *ctx) {
    if (ctx->current_token.type == TOKEN_ERROR) {
        return 0.0f;
    }
    
    if (ctx->current_token.type == TOKEN_NUMBER) {
        float value = ctx->current_token.value;
        next_token(ctx);
        return value;
    }
    
    if (ctx->current_token.type == TOKEN_VARIABLE) {
        float value;
        if (!formula_parser_get_variable(ctx->current_token.var_name, 
                                        ctx->variabili, ctx->num_variabili, &value)) {
            snprintf(ctx->error, sizeof(ctx->error), 
                    "Variable '%s' not found", ctx->current_token.var_name);
            ctx->current_token.type = TOKEN_ERROR;
            return 0.0f;
        }
        next_token(ctx);
        return value;
    }
    
    if (ctx->current_token.type == TOKEN_LPAREN) {
        next_token(ctx);
        float value = parse_expression(ctx);
        
        if (ctx->current_token.type != TOKEN_RPAREN) {
            snprintf(ctx->error, sizeof(ctx->error), "Expected ')'");
            ctx->current_token.type = TOKEN_ERROR;
            return 0.0f;
        }
        next_token(ctx);
        return value;
    }
    
    // Handle unary minus
    if (ctx->current_token.type == TOKEN_OPERATOR && ctx->current_token.op == '-') {
        next_token(ctx);
        return -parse_factor(ctx);
    }
    
    // Handle unary plus
    if (ctx->current_token.type == TOKEN_OPERATOR && ctx->current_token.op == '+') {
        next_token(ctx);
        return parse_factor(ctx);
    }
    
    snprintf(ctx->error, sizeof(ctx->error), "Unexpected token");
    ctx->current_token.type = TOKEN_ERROR;
    return 0.0f;
}

// Parse term: factor (* factor | / factor)*
static float parse_term(ParserContext *ctx) {
    float value = parse_factor(ctx);
    
    while (ctx->current_token.type == TOKEN_OPERATOR &&
           (ctx->current_token.op == '*' || ctx->current_token.op == '/')) {
        char op = ctx->current_token.op;
        next_token(ctx);
        
        float right = parse_factor(ctx);
        
        if (op == '*') {
            value *= right;
        } else {
            if (right == 0.0f) {
                snprintf(ctx->error, sizeof(ctx->error), "Division by zero");
                ctx->current_token.type = TOKEN_ERROR;
                return 0.0f;
            }
            value /= right;
        }
    }
    
    return value;
}

// Parse expression: term (+ term | - term)*
static float parse_expression(ParserContext *ctx) {
    float value = parse_term(ctx);
    
    while (ctx->current_token.type == TOKEN_OPERATOR &&
           (ctx->current_token.op == '+' || ctx->current_token.op == '-')) {
        char op = ctx->current_token.op;
        next_token(ctx);
        
        float right = parse_term(ctx);
        
        if (op == '+') {
            value += right;
        } else {
            value -= right;
        }
    }
    
    return value;
}

// Main evaluation function
ParseResult formula_parser_evaluate(const char *formula,
                                   const VariabileRilievo *variabili,
                                   uint8_t num_variabili) {
    ParseResult result = {
        .success = false,
        .value = 0.0f,
        .error_message = ""
    };
    
    if (!formula || !formula[0]) {
        snprintf(result.error_message, sizeof(result.error_message), "Empty formula");
        return result;
    }
    
    ParserContext ctx;
    init_parser(&ctx, formula, variabili, num_variabili);
    
    float value = parse_expression(&ctx);
    
    if (ctx.current_token.type == TOKEN_ERROR) {
        snprintf(result.error_message, sizeof(result.error_message), 
                "%s", ctx.error);
        ESP_LOGE(TAG, "Parse error: %s in formula: %s", ctx.error, formula);
        return result;
    }
    
    if (ctx.current_token.type != TOKEN_END) {
        snprintf(result.error_message, sizeof(result.error_message), 
                "Unexpected token at end");
        ESP_LOGE(TAG, "Unexpected token at end of formula: %s", formula);
        return result;
    }
    
    result.success = true;
    result.value = value;
    
    ESP_LOGI(TAG, "Formula '%s' evaluated to %.2f", formula, value);
    return result;
}

// Validate formula
bool formula_parser_validate(const char *formula) {
    if (!formula || !formula[0]) {
        return false;
    }
    
    // Create dummy variables for validation
    VariabileRilievo dummy_vars[4] = {
        {"L", "Larghezza", 1000.0f, true, true},
        {"H", "Altezza", 1000.0f, true, true},
        {"B", "Battuta", 50.0f, false, false},
        {"S", "Spessore", 20.0f, false, false}
    };
    
    ParseResult result = formula_parser_evaluate(formula, dummy_vars, 4);
    return result.success;
}

// Get variable value
bool formula_parser_get_variable(const char *nome,
                                const VariabileRilievo *variabili,
                                uint8_t num_variabili,
                                float *out_value) {
    if (!nome || !variabili || !out_value) {
        return false;
    }
    
    for (uint8_t i = 0; i < num_variabili; i++) {
        if (strcmp(variabili[i].nome, nome) == 0) {
            if (!variabili[i].rilevato) {
                ESP_LOGW(TAG, "Variable '%s' not measured yet", nome);
                return false;
            }
            *out_value = variabili[i].valore;
            return true;
        }
    }
    
    return false;
}

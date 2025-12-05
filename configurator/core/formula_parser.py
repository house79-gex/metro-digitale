"""
Parser e validatore per formule matematiche.
Supporta variabili, operatori aritmetici e funzioni matematiche base.
"""

import re
import math
from typing import Tuple, List, Dict, Union, Optional
from pyparsing import (
    Word, alphas, alphanums, nums, oneOf, opAssoc,
    infixNotation, Suppress, ParserElement, ParseException
)


class FormulaParser:
    """Parser per formule matematiche con variabili"""
    
    def __init__(self):
        # Abilita packrat parsing per performance
        ParserElement.enablePackrat()
        self._grammar = self._build_grammar()
        
    def _build_grammar(self):
        """Costruisce la grammatica per il parser"""
        # Numeri (interi e decimali)
        number = Word(nums + ".-").setParseAction(lambda t: float(t[0]))
        
        # Variabili (lettere maiuscole o nomi con underscore)
        variable = Word(alphas + "_", alphanums + "_")
        
        # Funzioni supportate
        func_name = oneOf("round abs min max", caseless=True)
        
        # Parentesi
        lparen = Suppress("(")
        rparen = Suppress(")")
        
        # Espressione di base
        expr = infixNotation(
            number | variable,
            [
                (func_name + lparen, 1, opAssoc.RIGHT),
                (rparen, 1, opAssoc.LEFT),
                (oneOf("* /"), 2, opAssoc.LEFT),
                (oneOf("+ -"), 2, opAssoc.LEFT),
            ]
        )
        
        return expr
    
    def parse(self, formula: str) -> Union[List, float]:
        """
        Effettua il parsing della formula
        
        Args:
            formula: Stringa contenente la formula
            
        Returns:
            AST (lista) o valore numerico
            
        Raises:
            ParseException: Se la formula non è valida
        """
        try:
            return self._grammar.parseString(formula, parseAll=True).asList()
        except ParseException as e:
            raise ValueError(f"Errore di parsing: {e}")
    
    def validate(self, formula: str, variabili: List[str]) -> Tuple[bool, str]:
        """
        Valida una formula controllando sintassi e variabili
        
        Args:
            formula: Formula da validare
            variabili: Lista di nomi variabili disponibili
            
        Returns:
            Tupla (valido, messaggio_errore)
        """
        if not formula or not formula.strip():
            return False, "Formula vuota"
        
        try:
            # Controlla sintassi
            self.parse(formula)
            
            # Controlla variabili utilizzate
            used_vars = self.get_variables(formula)
            invalid_vars = [v for v in used_vars if v not in variabili]
            
            if invalid_vars:
                return False, f"Variabili non definite: {', '.join(invalid_vars)}"
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def evaluate(self, formula: str, valori: Dict[str, float]) -> float:
        """
        Valuta una formula sostituendo le variabili con i valori forniti
        
        Args:
            formula: Formula da valutare
            valori: Dizionario nome_variabile -> valore
            
        Returns:
            Risultato numerico della formula
            
        Raises:
            ValueError: Se la formula non è valida o mancano variabili
        """
        # Ottieni variabili usate
        used_vars = self.get_variables(formula)
        
        # Controlla che tutte le variabili abbiano un valore
        missing = [v for v in used_vars if v not in valori]
        if missing:
            raise ValueError(f"Valori mancanti per: {', '.join(missing)}")
        
        # Sostituisci variabili e valuta
        try:
            # Crea namespace sicuro con funzioni matematiche
            safe_dict = {
                'round': round,
                'abs': abs,
                'min': min,
                'max': max,
                'math': math,
                '__builtins__': {}
            }
            safe_dict.update(valori)
            
            result = eval(formula, safe_dict)
            return float(result)
            
        except Exception as e:
            raise ValueError(f"Errore nella valutazione: {e}")
    
    def get_variables(self, formula: str) -> List[str]:
        """
        Estrae le variabili utilizzate nella formula
        
        Args:
            formula: Formula da analizzare
            
        Returns:
            Lista di nomi variabili (senza duplicati)
        """
        # Pattern per identificare variabili (lettere e underscore)
        pattern = r'\b([A-Za-z_][A-Za-z0-9_]*)\b'
        
        # Funzioni e keywords da escludere
        keywords = {'round', 'abs', 'min', 'max', 'math'}
        
        matches = re.findall(pattern, formula)
        variables = [m for m in matches if m.lower() not in keywords]
        
        # Rimuovi duplicati mantenendo ordine
        seen = set()
        unique_vars = []
        for var in variables:
            if var not in seen:
                seen.add(var)
                unique_vars.append(var)
        
        return unique_vars
    
    def test_formula(self, formula: str, test_values: Dict[str, float]) -> Tuple[bool, Union[float, str]]:
        """
        Testa una formula con valori di esempio
        
        Args:
            formula: Formula da testare
            test_values: Dizionario con valori di test
            
        Returns:
            Tupla (successo, risultato_o_errore)
        """
        try:
            result = self.evaluate(formula, test_values)
            return True, result
        except Exception as e:
            return False, str(e)

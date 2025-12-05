"""
Test per FormulaParser
"""

import pytest
from core.formula_parser import FormulaParser


def test_formula_parser_init():
    """Test inizializzazione parser"""
    parser = FormulaParser()
    assert parser is not None


def test_parse_simple_expression():
    """Test parsing espressione semplice"""
    parser = FormulaParser()
    
    # Numero semplice
    result = parser.parse("42")
    assert result is not None
    
    # Somma
    result = parser.parse("10 + 5")
    assert result is not None


def test_validate_formula():
    """Test validazione formula"""
    parser = FormulaParser()
    
    # Formula valida
    valid, msg = parser.validate("(L + 6) / 2", ["L", "H", "B"])
    assert valid is True
    assert msg == ""
    
    # Formula con variabile non definita
    valid, msg = parser.validate("L + X", ["L", "H"])
    assert valid is False
    assert "non definite" in msg.lower()
    
    # Formula vuota
    valid, msg = parser.validate("", ["L"])
    assert valid is False


def test_evaluate_formula():
    """Test valutazione formula"""
    parser = FormulaParser()
    
    # Formula semplice
    result = parser.evaluate("(L + 6) / 2", {"L": 1200})
    assert result == 603.0
    
    # Formula con sottrazione
    result = parser.evaluate("H - 10", {"H": 2000})
    assert result == 1990.0
    
    # Formula con round
    result = parser.evaluate("round((L + B) / 2)", {"L": 1000, "B": 50})
    assert result == 525.0


def test_evaluate_missing_variable():
    """Test valutazione con variabile mancante"""
    parser = FormulaParser()
    
    with pytest.raises(ValueError) as exc_info:
        parser.evaluate("L + H", {"L": 100})
    
    assert "mancanti" in str(exc_info.value).lower()


def test_get_variables():
    """Test estrazione variabili"""
    parser = FormulaParser()
    
    # Formula con più variabili
    vars = parser.get_variables("(L + H) * B / 2")
    assert set(vars) == {"L", "H", "B"}
    
    # Formula con variabile ripetuta
    vars = parser.get_variables("L + L + H")
    assert set(vars) == {"L", "H"}
    
    # Formula senza variabili
    vars = parser.get_variables("42 + 10")
    assert len(vars) == 0


def test_test_formula():
    """Test metodo test_formula"""
    parser = FormulaParser()
    
    # Test con successo
    success, result = parser.test_formula("L + 10", {"L": 100})
    assert success is True
    assert result == 110.0
    
    # Test con errore
    success, result = parser.test_formula("L / 0", {"L": 100})
    assert success is False
    assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

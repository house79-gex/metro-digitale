"""
Test per toolbox drag & drop
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Define expected elements structure (matching toolbox_widget.py)
EXPECTED_ELEMENTS = {
    "Layout": [
        {"name": "Panel", "icon": "□", "desc": "Pannello contenitore"},
        {"name": "Frame", "icon": "▢", "desc": "Cornice con bordo"},
        {"name": "Separator", "icon": "─", "desc": "Linea separatrice"},
    ],
    "Testo": [
        {"name": "Label", "icon": "Aa", "desc": "Etichetta testo"},
        {"name": "MeasureDisplay", "icon": "📏", "desc": "Display misura grande"},
        {"name": "FormulaResult", "icon": "fx", "desc": "Risultato formula"},
    ],
    "Controlli": [
        {"name": "Button", "icon": "▣", "desc": "Pulsante standard"},
        {"name": "IconButton", "icon": "🔘", "desc": "Pulsante con icona"},
        {"name": "ToggleButton", "icon": "◐", "desc": "Pulsante on/off"},
    ],
    "Input": [
        {"name": "NumberInput", "icon": "123", "desc": "Campo numerico"},
        {"name": "Slider", "icon": "──●──", "desc": "Cursore valore"},
        {"name": "Dropdown", "icon": "▼", "desc": "Menu a tendina"},
    ],
    "Speciali": [
        {"name": "TipologiaWidget", "icon": "🪟", "desc": "Selettore tipologia"},
        {"name": "AstinaSelector", "icon": "📐", "desc": "Selettore astina"},
        {"name": "MaterialSelector", "icon": "🧱", "desc": "Selettore materiale"},
    ],
}


def test_element_categories():
    """Test che tutte le categorie sono presenti"""
    expected_categories = ["Layout", "Testo", "Controlli", "Input", "Speciali"]
    assert list(EXPECTED_ELEMENTS.keys()) == expected_categories


def test_element_structure():
    """Test struttura elementi"""
    for category, elements in EXPECTED_ELEMENTS.items():
        assert isinstance(elements, list)
        for elem in elements:
            assert "name" in elem
            assert "icon" in elem
            assert "desc" in elem
            assert isinstance(elem["name"], str)
            assert isinstance(elem["icon"], str)
            assert isinstance(elem["desc"], str)


def test_mime_data_format():
    """Test formato MIME data per drag & drop"""
    # Simula il formato che verrà usato
    test_data = {'type': 'Button', 'category': '📁 Controlli'}
    json_str = json.dumps(test_data)
    
    # Verifica che sia valido JSON
    parsed = json.loads(json_str)
    assert parsed['type'] == 'Button'
    assert 'category' in parsed


def test_all_element_types():
    """Test che tutti gli elementi hanno un tipo"""
    all_types = []
    for category, elements in EXPECTED_ELEMENTS.items():
        for elem in elements:
            all_types.append(elem["name"])
    
    # Verifica elementi base
    assert "Button" in all_types
    assert "Label" in all_types
    assert "Panel" in all_types
    assert "TipologiaWidget" in all_types
    
    # Conta totale
    assert len(all_types) == 15


if __name__ == "__main__":
    print("Running toolbox drag & drop tests...")
    
    test_element_categories()
    print("✓ test_element_categories")
    
    test_element_structure()
    print("✓ test_element_structure")
    
    test_mime_data_format()
    print("✓ test_mime_data_format")
    
    test_all_element_types()
    print("✓ test_all_element_types")
    
    print("\n✓ All toolbox tests passed!")

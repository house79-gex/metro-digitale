"""
Test per template JSON preimpostati
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_templates_exist():
    """Test che tutti i template esistano"""
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / "resources" / "templates"
    
    required_templates = [
        "home_standard.json",
        "calibro_semplice.json",
        "calibro_avanzato.json",
        "vetri_lxa.json",
        "vetri_con_battute.json",
        "astine_anta_ribalta.json",
        "fermavetri_standard.json",
        "tipologia_finestra_1a.json",
        "tipologia_finestra_2a.json",
        "impostazioni.json"
    ]
    
    for template_name in required_templates:
        template_path = templates_dir / template_name
        assert template_path.exists(), f"Template not found: {template_name}"


def test_templates_valid_json():
    """Test che tutti i template siano JSON validi"""
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / "resources" / "templates"
    
    for template_file in templates_dir.glob("*.json"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert isinstance(data, dict), f"Template {template_file.name} is not a dictionary"
        except json.JSONDecodeError as e:
            assert False, f"Invalid JSON in {template_file.name}: {e}"


def test_template_structure():
    """Test struttura base dei template"""
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / "resources" / "templates"
    
    for template_file in templates_dir.glob("*.json"):
        with open(template_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Verifica campi obbligatori
            assert 'name' in data, f"Missing 'name' in {template_file.name}"
            assert 'description' in data, f"Missing 'description' in {template_file.name}"
            assert 'elements' in data, f"Missing 'elements' in {template_file.name}"
            assert isinstance(data['elements'], list), f"'elements' not a list in {template_file.name}"


def test_template_elements_structure():
    """Test struttura elementi nei template"""
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / "resources" / "templates"
    
    for template_file in templates_dir.glob("*.json"):
        with open(template_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            for element in data['elements']:
                # Verifica campi obbligatori elemento
                assert 'type' in element, f"Element missing 'type' in {template_file.name}"
                assert 'id' in element, f"Element missing 'id' in {template_file.name}"
                assert 'x' in element, f"Element missing 'x' in {template_file.name}"
                assert 'y' in element, f"Element missing 'y' in {template_file.name}"
                assert 'width' in element, f"Element missing 'width' in {template_file.name}"
                assert 'height' in element, f"Element missing 'height' in {template_file.name}"
                assert 'properties' in element, f"Element missing 'properties' in {template_file.name}"


def test_home_standard_template():
    """Test specifico per template home_standard"""
    base_dir = Path(__file__).parent.parent
    template_path = base_dir / "resources" / "templates" / "home_standard.json"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data['name'] == "Home Standard"
    assert len(data['elements']) >= 5  # Almeno 5 elementi nella home
    
    # Verifica che ci sia un display principale
    display_found = False
    for element in data['elements']:
        if element['type'] == 'MeasureDisplay':
            display_found = True
            break
    assert display_found, "MeasureDisplay not found in home_standard"


def test_calibro_templates():
    """Test template calibro"""
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / "resources" / "templates"
    
    # Calibro semplice
    with open(templates_dir / "calibro_semplice.json", 'r', encoding='utf-8') as f:
        calibro_semplice = json.load(f)
    
    assert "Calibro" in calibro_semplice['name']
    assert len(calibro_semplice['elements']) >= 4
    
    # Calibro avanzato
    with open(templates_dir / "calibro_avanzato.json", 'r', encoding='utf-8') as f:
        calibro_avanzato = json.load(f)
    
    assert "Avanzato" in calibro_avanzato['name']
    # Calibro avanzato dovrebbe avere più elementi del semplice
    assert len(calibro_avanzato['elements']) > len(calibro_semplice['elements'])


def test_tooltips_exist():
    """Test che il file tooltips.json esista"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    assert tooltips_path.exists(), "tooltips.json not found"


def test_tooltips_valid_json():
    """Test che tooltips.json sia JSON valido"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert 'tooltips' in data


def test_tooltips_structure():
    """Test struttura tooltips.json"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tooltips = data['tooltips']
    
    # Verifica categorie principali
    assert 'canvas' in tooltips
    assert 'toolbox' in tooltips
    assert 'properties' in tooltips
    assert 'elements' in tooltips
    assert 'menus' in tooltips
    assert 'hardware' in tooltips


if __name__ == "__main__":
    print("Running template tests...")
    
    test_templates_exist()
    print("✓ test_templates_exist")
    
    test_templates_valid_json()
    print("✓ test_templates_valid_json")
    
    test_template_structure()
    print("✓ test_template_structure")
    
    test_template_elements_structure()
    print("✓ test_template_elements_structure")
    
    test_home_standard_template()
    print("✓ test_home_standard_template")
    
    test_calibro_templates()
    print("✓ test_calibro_templates")
    
    test_tooltips_exist()
    print("✓ test_tooltips_exist")
    
    test_tooltips_valid_json()
    print("✓ test_tooltips_valid_json")
    
    test_tooltips_structure()
    print("✓ test_tooltips_structure")
    
    print("\n✓ All template tests passed!")

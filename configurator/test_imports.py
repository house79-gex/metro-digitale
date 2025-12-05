#!/usr/bin/env python3
"""
Test script per verificare che tutti i moduli core possano essere importati
"""

import sys
import os

# Aggiungi directory al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_core_imports():
    """Test import moduli core"""
    print("Testing core imports...")
    
    try:
        from core.config_model import (
            VariabileRilievo, ElementoCalcolato, TipologiaInfisso,
            MenuItem, AstinaConfig, FermavetroConfig, ProgettoConfigurazione
        )
        print("✓ config_model imported")
    except Exception as e:
        print(f"✗ config_model import failed: {e}")
        return False
    
    try:
        from core.formula_parser import FormulaParser
        print("✓ formula_parser imported")
    except Exception as e:
        print(f"✗ formula_parser import failed: {e}")
        return False
    
    try:
        from core.project_manager import ProjectManager
        print("✓ project_manager imported")
    except Exception as e:
        print(f"✗ project_manager import failed: {e}")
        return False
    
    try:
        from core.esp_uploader import ESPUploader
        print("✓ esp_uploader imported")
    except Exception as e:
        print(f"✗ esp_uploader import failed: {e}")
        return False
    
    try:
        from core.icon_browser import IconifyClient, IconInfo
        print("✓ icon_browser imported")
    except Exception as e:
        print(f"✗ icon_browser import failed: {e}")
        return False
    
    try:
        from core.color_palette import ColorPaletteGenerator
        print("✓ color_palette imported")
    except Exception as e:
        print(f"✗ color_palette import failed: {e}")
        return False
    
    return True


def test_core_functionality():
    """Test funzionalità base dei moduli"""
    print("\nTesting core functionality...")
    
    from core.config_model import ProgettoConfigurazione, MenuItem
    from core.formula_parser import FormulaParser
    from core.project_manager import ProjectManager
    from core.color_palette import ColorPaletteGenerator
    
    # Test creazione progetto
    try:
        progetto = ProgettoConfigurazione(nome="Test")
        print(f"✓ Created project: {progetto.nome}")
    except Exception as e:
        print(f"✗ Project creation failed: {e}")
        return False
    
    # Test formula parser
    try:
        parser = FormulaParser()
        result = parser.evaluate("(L + 6) / 2", {"L": 1200})
        assert result == 603.0
        print(f"✓ Formula parser works: (1200 + 6) / 2 = {result}")
    except Exception as e:
        print(f"✗ Formula parser failed: {e}")
        return False
    
    # Test color palette
    try:
        gen = ColorPaletteGenerator()
        comp = gen.get_complementary("#00ff88")
        print(f"✓ Color palette works: complementary of #00ff88 is {comp}")
    except Exception as e:
        print(f"✗ Color palette failed: {e}")
        return False
    
    # Test project manager
    try:
        manager = ProjectManager()
        proj = manager.new_project("Test Project")
        print(f"✓ Project manager works: created {proj.nome}")
    except Exception as e:
        print(f"✗ Project manager failed: {e}")
        return False
    
    return True


def main():
    """Main test function"""
    print("=" * 60)
    print("Metro Digitale Configurator - Import and Functionality Tests")
    print("=" * 60)
    
    success = True
    
    if not test_core_imports():
        success = False
    
    if not test_core_functionality():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Test per IOManager
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
import tempfile
import json
from core.io_manager import IOManager


def test_io_manager_init():
    """Test inizializzazione IOManager"""
    manager = IOManager()
    
    assert manager.last_export_path is None
    assert manager.last_import_path is None


def test_export_import_measures_jsonl():
    """Test export/import misure JSONL"""
    manager = IOManager()
    
    # Dati test
    measures = [
        {"value": 123.45, "unit": "mm", "probe": "internal"},
        {"value": 678.90, "unit": "mm", "probe": "external"}
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "measures.jsonl"
        
        # Export
        result = manager.export_measures_jsonl(measures, output_path, append=False)
        assert result is True
        assert output_path.exists()
        
        # Import
        imported = manager.import_measures_jsonl(output_path)
        assert imported is not None
        assert len(imported) == 2
        assert imported[0]["value"] == 123.45
        
        # Test append
        more_measures = [{"value": 111.22, "unit": "mm", "probe": "depth"}]
        result = manager.export_measures_jsonl(more_measures, output_path, append=True)
        assert result is True
        
        imported_all = manager.import_measures_jsonl(output_path)
        assert len(imported_all) == 3


def test_export_import_measures_csv():
    """Test export/import misure CSV"""
    manager = IOManager()
    
    measures = [
        {"value": 123.45, "unit": "mm", "probe": "internal"},
        {"value": 678.90, "unit": "mm", "probe": "external"}
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "measures.csv"
        
        # Export
        result = manager.export_measures_csv(measures, output_path)
        assert result is True
        assert output_path.exists()
        
        # Import
        imported = manager.import_measures_csv(output_path)
        assert imported is not None
        assert len(imported) == 2
        assert float(imported[0]["value"]) == 123.45


def test_export_import_config():
    """Test export/import configurazione"""
    manager = IOManager()
    
    config = {
        "schema_version": "2.0.0",
        "hardware": {
            "encoder": {"resolution": 0.01}
        },
        "modes": [],
        "ui_layout": {"theme": "dark"}
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "config.json"
        
        # Export
        result = manager.export_config(config, output_path, create_backup=False)
        assert result is True
        assert output_path.exists()
        
        # Import
        imported = manager.import_config(output_path, migrate=False)
        assert imported is not None
        assert imported["schema_version"] == "2.0.0"


def test_config_migration():
    """Test migrazione configurazione"""
    manager = IOManager()
    
    # Config vecchio senza schema_version
    old_config = {
        "version": "1.0.0",
        "nome": "Test"
    }
    
    migrated = manager._migrate_config(old_config.copy())
    
    # Verifica campi aggiunti
    assert "schema_version" in migrated
    assert "hardware" in migrated
    assert "modes" in migrated
    assert "ui_layout" in migrated
    assert "icons" in migrated


def test_list_export_destinations():
    """Test elenco destinazioni export"""
    manager = IOManager()
    
    destinations = manager.list_export_destinations()
    
    assert isinstance(destinations, list)
    assert len(destinations) >= 3  # local, sd, usb
    
    # Verifica locale sempre disponibile
    local_dest = [d for d in destinations if d["type"] == "local"]
    assert len(local_dest) == 1
    assert local_dest[0]["available"] is True


def test_path_helpers():
    """Test helper percorsi"""
    manager = IOManager()
    
    sd_path = manager.get_sd_path("test.json")
    assert "test.json" in str(sd_path)
    
    usb_path = manager.get_usb_path("test.json")
    assert "test.json" in str(usb_path)
    
    # Questi possono essere False su Windows
    is_sd = manager.is_sd_available()
    is_usb = manager.is_usb_available()
    assert isinstance(is_sd, bool)
    assert isinstance(is_usb, bool)


def test_singleton_pattern():
    """Test pattern singleton"""
    from core.io_manager import get_io_manager
    
    manager1 = get_io_manager()
    manager2 = get_io_manager()
    
    # Dovrebbero essere la stessa istanza
    assert manager1 is manager2


if __name__ == "__main__":
    print("Running IOManager tests...")
    
    test_io_manager_init()
    print("✓ test_io_manager_init")
    
    test_export_import_measures_jsonl()
    print("✓ test_export_import_measures_jsonl")
    
    test_export_import_measures_csv()
    print("✓ test_export_import_measures_csv")
    
    test_export_import_config()
    print("✓ test_export_import_config")
    
    test_config_migration()
    print("✓ test_config_migration")
    
    test_list_export_destinations()
    print("✓ test_list_export_destinations")
    
    test_path_helpers()
    print("✓ test_path_helpers")
    
    test_singleton_pattern()
    print("✓ test_singleton_pattern")
    
    print("\n✓ All IOManager tests passed!")

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


def test_io_manager_export_import_jsonl():
    """Test export/import misure JSONL"""
    manager = IOManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "measures.jsonl"
        
        # Crea misure test
        measures = manager.create_example_measures(5)
        
        # Export
        success = manager.export_measures_jsonl(measures, filepath)
        assert success
        assert filepath.exists()
        
        # Import
        imported = manager.import_measures_jsonl(filepath)
        assert imported is not None
        assert len(imported) == 5
        
        # Verifica contenuto
        for i, measure in enumerate(imported):
            assert measure['id'] == i + 1


def test_io_manager_append_jsonl():
    """Test append JSONL"""
    manager = IOManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "measures.jsonl"
        
        # Prima scrittura
        measures1 = manager.create_example_measures(3)
        manager.export_measures_jsonl(measures1, filepath)
        
        # Append
        measures2 = manager.create_example_measures(2)
        manager.export_measures_jsonl(measures2, filepath, append=True)
        
        # Import
        imported = manager.import_measures_jsonl(filepath)
        assert len(imported) == 5


def test_io_manager_export_import_csv():
    """Test export/import misure CSV"""
    manager = IOManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "measures.csv"
        
        # Crea misure test
        measures = manager.create_example_measures(3)
        
        # Export
        success = manager.export_measures_csv(measures, filepath)
        assert success
        assert filepath.exists()
        
        # Import
        imported = manager.import_measures_csv(filepath)
        assert imported is not None
        assert len(imported) == 3


def test_io_manager_export_import_config():
    """Test export/import configurazione"""
    manager = IOManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "config.json"
        
        # Crea config test
        config = {
            'schema_version': '1.0.0',
            'hardware': {'encoder': {}},
            'modes': [],
            'ui_layout': {'theme': 'dark'}
        }
        
        # Export
        success = manager.export_config(config, filepath)
        assert success
        assert filepath.exists()
        
        # Import
        imported = manager.import_config(filepath)
        assert imported is not None
        assert imported['schema_version'] == '1.0.0'
        assert 'hardware' in imported


def test_io_manager_config_migration():
    """Test migrazione schema configurazione"""
    manager = IOManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "config.json"
        
        # Crea config vecchia versione
        old_config = {
            'version': '1.0.0',
            'nome': 'Test'
        }
        
        with open(filepath, 'w') as f:
            json.dump(old_config, f)
        
        # Import con migrazione
        imported = manager.import_config(filepath, migrate=True)
        
        # Verifica campi aggiunti
        assert 'schema_version' in imported
        assert 'hardware' in imported
        assert 'modes' in imported
        assert 'ui_layout' in imported


def test_io_manager_validate_config():
    """Test validazione configurazione"""
    manager = IOManager()
    
    # Config valida
    valid_config = {
        'schema_version': '1.0.0',
        'hardware': {},
        'modes': [],
        'ui_layout': {}
    }
    
    is_valid, errors = manager.validate_config(valid_config)
    assert is_valid
    assert len(errors) == 0
    
    # Config invalida
    invalid_config = {
        'schema_version': '1.0.0'
    }
    
    is_valid, errors = manager.validate_config(invalid_config)
    assert not is_valid
    assert len(errors) > 0


def test_io_manager_backup_config():
    """Test backup configurazione"""
    manager = IOManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "config.json"
        
        # Crea config iniziale
        config1 = {'schema_version': '1.0.0', 'hardware': {}, 'modes': [], 'ui_layout': {}}
        manager.export_config(config1, filepath)
        
        # Export con backup
        config2 = {'schema_version': '1.0.0', 'hardware': {'test': True}, 'modes': [], 'ui_layout': {}}
        manager.export_config(config2, filepath, create_backup=True)
        
        # Verifica backup
        backup_file = filepath.with_suffix('.json.bak')
        assert backup_file.exists()


if __name__ == "__main__":
    print("Running IOManager tests...")
    
    test_io_manager_export_import_jsonl()
    print("✓ test_io_manager_export_import_jsonl")
    
    test_io_manager_append_jsonl()
    print("✓ test_io_manager_append_jsonl")
    
    test_io_manager_export_import_csv()
    print("✓ test_io_manager_export_import_csv")
    
    test_io_manager_export_import_config()
    print("✓ test_io_manager_export_import_config")
    
    test_io_manager_config_migration()
    print("✓ test_io_manager_config_migration")
    
    test_io_manager_validate_config()
    print("✓ test_io_manager_validate_config")
    
    test_io_manager_backup_config()
    print("✓ test_io_manager_backup_config")
    
    print("\nAll tests passed!")

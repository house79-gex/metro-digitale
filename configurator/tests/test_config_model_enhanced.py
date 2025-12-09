"""
Test per enhanced config_model con nuovi campi
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.config_model import (
    ProgettoConfigurazione, HardwareConfig, ModeConfig, UILayout
)


def test_hardware_config_creation():
    """Test creazione HardwareConfig"""
    hw = HardwareConfig()
    
    assert 'encoder' in hw.to_dict()
    assert 'probes' in hw.to_dict()
    assert 'bluetooth' in hw.to_dict()
    assert 'display' in hw.to_dict()


def test_hardware_config_to_dict():
    """Test serializzazione HardwareConfig"""
    hw = HardwareConfig()
    hw.encoder['resolution'] = 0.02
    
    data = hw.to_dict()
    assert data['encoder']['resolution'] == 0.02


def test_hardware_config_from_dict():
    """Test deserializzazione HardwareConfig"""
    data = {
        'encoder': {'resolution': 0.05},
        'probes': [{'id': 'test', 'name': 'Test'}],
        'bluetooth': {'name': 'Test'},
        'display': {'width': 1024}
    }
    
    hw = HardwareConfig.from_dict(data)
    assert hw.encoder['resolution'] == 0.05
    assert len(hw.probes) == 1


def test_mode_config_creation():
    """Test creazione ModeConfig"""
    mode = ModeConfig(
        id='test_mode',
        name='Test Mode',
        category='Test'
    )
    
    assert mode.id == 'test_mode'
    assert mode.name == 'Test Mode'
    assert mode.unit == 'mm'
    assert mode.decimals == 2


def test_mode_config_with_workflow():
    """Test ModeConfig con workflow"""
    mode = ModeConfig(
        id='finestra',
        name='Finestra',
        workflow=[
            {'step': 1, 'variable': 'L', 'description': 'Larghezza'},
            {'step': 2, 'variable': 'H', 'description': 'Altezza'}
        ],
        formula='L + H'
    )
    
    data = mode.to_dict()
    assert len(data['workflow']) == 2
    assert data['formula'] == 'L + H'


def test_mode_config_bluetooth():
    """Test ModeConfig con Bluetooth"""
    mode = ModeConfig(
        id='test',
        name='Test',
        bt_enabled=True,
        bt_format='JSON',
        bt_payload_template='{"result": {result}}'
    )
    
    data = mode.to_dict()
    assert data['bt_enabled'] is True
    assert data['bt_format'] == 'JSON'


def test_ui_layout_creation():
    """Test creazione UILayout"""
    ui = UILayout()
    
    assert ui.theme == 'dark'
    assert ui.units == 'mm'
    assert ui.decimals == 2
    assert ui.language == 'it'


def test_ui_layout_custom():
    """Test UILayout personalizzato"""
    ui = UILayout(
        theme='light',
        units='cm',
        decimals=3,
        language='en'
    )
    
    data = ui.to_dict()
    assert data['theme'] == 'light'
    assert data['units'] == 'cm'
    assert data['decimals'] == 3


def test_progetto_with_schema_version():
    """Test ProgettoConfigurazione con schema_version"""
    prog = ProgettoConfigurazione()
    
    assert prog.schema_version == '1.0.0'
    assert isinstance(prog.hardware, HardwareConfig)
    assert isinstance(prog.modes, list)
    assert isinstance(prog.ui_layout, UILayout)


def test_progetto_to_dict_complete():
    """Test serializzazione completa ProgettoConfigurazione"""
    prog = ProgettoConfigurazione()
    prog.nome = "Test Project"
    
    # Aggiungi mode
    mode = ModeConfig(id='test', name='Test')
    prog.modes.append(mode)
    
    data = prog.to_dict()
    
    # Verifica nuovi campi
    assert 'schema_version' in data
    assert 'hardware' in data
    assert 'modes' in data
    assert 'ui_layout' in data
    assert 'icons' in data
    
    # Verifica campi esistenti
    assert 'menus' in data
    assert 'tipologie' in data
    assert 'astine' in data
    assert 'fermavetri' in data
    
    # Verifica contenuto
    assert len(data['modes']) == 1
    assert data['modes'][0]['id'] == 'test'


def test_progetto_from_dict_with_new_fields():
    """Test deserializzazione ProgettoConfigurazione con nuovi campi"""
    data = {
        'schema_version': '1.0.0',
        'version': '1.0.0',
        'nome': 'Test',
        'created': '2025-01-01T00:00:00',
        'modified': '2025-01-01T00:00:00',
        'hardware': {
            'encoder': {'resolution': 0.01},
            'probes': [],
            'bluetooth': {},
            'display': {}
        },
        'modes': [
            {
                'id': 'test',
                'name': 'Test Mode',
                'workflow': [],
                'formula': 'L + H'
            }
        ],
        'ui_layout': {
            'theme': 'dark',
            'units': 'mm'
        },
        'icons': {},
        'menus': [],
        'tipologie': [],
        'astine': [],
        'fermavetri': [],
        'impostazioni': {}
    }
    
    prog = ProgettoConfigurazione.from_dict(data)
    
    assert prog.schema_version == '1.0.0'
    assert len(prog.modes) == 1
    assert prog.modes[0].id == 'test'
    assert prog.hardware.encoder['resolution'] == 0.01


def test_progetto_backward_compatibility():
    """Test compatibilità con vecchie configurazioni"""
    # Config senza nuovi campi
    data = {
        'version': '1.0.0',
        'nome': 'Old Config',
        'created': '2025-01-01T00:00:00',
        'modified': '2025-01-01T00:00:00',
        'menus': [],
        'tipologie': [],
        'astine': [],
        'fermavetri': [],
        'impostazioni': {}
    }
    
    # Dovrebbe caricare con default
    prog = ProgettoConfigurazione.from_dict(data)
    
    assert prog.schema_version == '1.0.0'  # Default
    assert isinstance(prog.hardware, HardwareConfig)
    assert isinstance(prog.modes, list)
    assert isinstance(prog.ui_layout, UILayout)


if __name__ == "__main__":
    print("Running enhanced config_model tests...")
    
    test_hardware_config_creation()
    print("✓ test_hardware_config_creation")
    
    test_hardware_config_to_dict()
    print("✓ test_hardware_config_to_dict")
    
    test_hardware_config_from_dict()
    print("✓ test_hardware_config_from_dict")
    
    test_mode_config_creation()
    print("✓ test_mode_config_creation")
    
    test_mode_config_with_workflow()
    print("✓ test_mode_config_with_workflow")
    
    test_mode_config_bluetooth()
    print("✓ test_mode_config_bluetooth")
    
    test_ui_layout_creation()
    print("✓ test_ui_layout_creation")
    
    test_ui_layout_custom()
    print("✓ test_ui_layout_custom")
    
    test_progetto_with_schema_version()
    print("✓ test_progetto_with_schema_version")
    
    test_progetto_to_dict_complete()
    print("✓ test_progetto_to_dict_complete")
    
    test_progetto_from_dict_with_new_fields()
    print("✓ test_progetto_from_dict_with_new_fields")
    
    test_progetto_backward_compatibility()
    print("✓ test_progetto_backward_compatibility")
    
    print("\nAll tests passed!")

"""
Test per configurazione hardware Metro Digitale
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.hardware_config import (
    EncoderConfig, PuntaleConfig, ModalitaOperativa, BluetoothConfig, 
    HardwareConfig, TipoPuntale, ModalitaMisura
)


def test_encoder_config_creation():
    """Test creazione configurazione encoder"""
    encoder = EncoderConfig()
    assert encoder.risoluzione == 400
    assert encoder.pin_clk == 2
    assert encoder.pin_dt == 3
    assert encoder.fattore_calibrazione == 1.0


def test_encoder_config_to_dict():
    """Test conversione encoder a dizionario"""
    encoder = EncoderConfig(risoluzione=600, pin_clk=5)
    data = encoder.to_dict()
    assert data['risoluzione'] == 600
    assert data['pin_clk'] == 5


def test_encoder_config_from_dict():
    """Test creazione encoder da dizionario"""
    data = {
        'risoluzione': 800,
        'pin_clk': 10,
        'pin_dt': 11,
        'pin_sw': 12,
        'fattore_calibrazione': 1.5
    }
    encoder = EncoderConfig.from_dict(data)
    assert encoder.risoluzione == 800
    assert encoder.fattore_calibrazione == 1.5


def test_puntale_config_presets():
    """Test puntali preimpostati"""
    presets = PuntaleConfig.get_presets()
    assert len(presets) == 5
    assert presets[0].tipo == TipoPuntale.STANDARD
    assert presets[1].tipo == TipoPuntale.INTERNO


def test_puntale_config_to_from_dict():
    """Test conversione puntale a/da dizionario"""
    puntale = PuntaleConfig(
        tipo=TipoPuntale.ESTERNO,
        nome="Test Puntale",
        offset_mm=5.0
    )
    data = puntale.to_dict()
    assert data['tipo'] == 'esterno'
    assert data['offset_mm'] == 5.0
    
    restored = PuntaleConfig.from_dict(data)
    assert restored.tipo == TipoPuntale.ESTERNO
    assert restored.offset_mm == 5.0


def test_modalita_operativa_presets():
    """Test modalità operative preimpostate"""
    presets = ModalitaOperativa.get_presets()
    assert len(presets) == 5
    assert presets[0].modalita == ModalitaMisura.CALIBRO
    assert presets[1].modalita == ModalitaMisura.VETRI


def test_modalita_operativa_to_from_dict():
    """Test conversione modalità a/da dizionario"""
    modalita = ModalitaOperativa(
        modalita=ModalitaMisura.ASTINE,
        nome="Test Modalità",
        parametri={"test": "value"}
    )
    data = modalita.to_dict()
    assert data['modalita'] == 'astine'
    assert data['parametri']['test'] == 'value'
    
    restored = ModalitaOperativa.from_dict(data)
    assert restored.modalita == ModalitaMisura.ASTINE


def test_bluetooth_config():
    """Test configurazione Bluetooth"""
    bt = BluetoothConfig()
    assert bt.abilitato is True
    assert bt.nome_dispositivo == "MetroDigitale"
    assert bt.protocollo == "BLE"


def test_bluetooth_config_to_from_dict():
    """Test conversione Bluetooth a/da dizionario"""
    bt = BluetoothConfig(nome_dispositivo="TestDevice", timeout_s=60)
    data = bt.to_dict()
    assert data['nome_dispositivo'] == "TestDevice"
    assert data['timeout_s'] == 60
    
    restored = BluetoothConfig.from_dict(data)
    assert restored.nome_dispositivo == "TestDevice"


def test_hardware_config_creation():
    """Test creazione configurazione hardware completa"""
    hw = HardwareConfig()
    assert hw.encoder is not None
    assert len(hw.puntali) > 0
    assert hw.puntale_corrente is not None
    assert len(hw.modalita) > 0
    assert hw.modalita_corrente is not None
    assert hw.bluetooth is not None


def test_hardware_config_to_from_dict():
    """Test conversione hardware completo a/da dizionario"""
    hw = HardwareConfig()
    data = hw.to_dict()
    
    assert 'encoder' in data
    assert 'puntali' in data
    assert 'bluetooth' in data
    
    restored = HardwareConfig.from_dict(data)
    assert restored.encoder.risoluzione == hw.encoder.risoluzione
    assert len(restored.puntali) == len(hw.puntali)


def test_hardware_config_default():
    """Test configurazione hardware predefinita"""
    hw = HardwareConfig.get_default()
    assert hw.encoder.risoluzione == 400
    assert len(hw.puntali) == 5
    assert len(hw.modalita) == 5


if __name__ == "__main__":
    print("Running hardware config tests...")
    
    test_encoder_config_creation()
    print("✓ test_encoder_config_creation")
    
    test_encoder_config_to_dict()
    print("✓ test_encoder_config_to_dict")
    
    test_encoder_config_from_dict()
    print("✓ test_encoder_config_from_dict")
    
    test_puntale_config_presets()
    print("✓ test_puntale_config_presets")
    
    test_puntale_config_to_from_dict()
    print("✓ test_puntale_config_to_from_dict")
    
    test_modalita_operativa_presets()
    print("✓ test_modalita_operativa_presets")
    
    test_modalita_operativa_to_from_dict()
    print("✓ test_modalita_operativa_to_from_dict")
    
    test_bluetooth_config()
    print("✓ test_bluetooth_config")
    
    test_bluetooth_config_to_from_dict()
    print("✓ test_bluetooth_config_to_from_dict")
    
    test_hardware_config_creation()
    print("✓ test_hardware_config_creation")
    
    test_hardware_config_to_from_dict()
    print("✓ test_hardware_config_to_from_dict")
    
    test_hardware_config_default()
    print("✓ test_hardware_config_default")
    
    print("\n✓ All hardware config tests passed!")

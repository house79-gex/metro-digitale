"""
Test per config_model
"""

import pytest
from datetime import datetime
from core.config_model import (
    VariabileRilievo, ElementoCalcolato, TipologiaInfisso,
    MenuItem, AstinaConfig, FermavetroConfig, ProgettoConfigurazione
)


def test_variabile_rilievo():
    """Test VariabileRilievo"""
    var = VariabileRilievo(
        nome="L",
        descrizione="Larghezza",
        obbligatoria=True,
        valore_test=1200.0
    )
    
    assert var.nome == "L"
    assert var.descrizione == "Larghezza"
    assert var.obbligatoria is True
    assert var.valore_test == 1200.0
    
    # Test serializzazione
    data = var.to_dict()
    assert data["nome"] == "L"
    
    # Test deserializzazione
    var2 = VariabileRilievo.from_dict(data)
    assert var2.nome == var.nome


def test_elemento_calcolato():
    """Test ElementoCalcolato"""
    elem = ElementoCalcolato(
        nome="Traversa",
        formula="(L + 6) / 2",
        quantita=2,
        colore="#00ff88"
    )
    
    assert elem.nome == "Traversa"
    assert elem.formula == "(L + 6) / 2"
    assert elem.quantita == 2
    
    # Test serializzazione/deserializzazione
    data = elem.to_dict()
    elem2 = ElementoCalcolato.from_dict(data)
    assert elem2.formula == elem.formula


def test_tipologia_infisso():
    """Test TipologiaInfisso"""
    tip = TipologiaInfisso(
        id="fin_2_ante",
        nome="Finestra 2 Ante",
        icona="mdi:window",
        categoria="Finestre"
    )
    
    assert tip.id == "fin_2_ante"
    assert tip.nome == "Finestra 2 Ante"
    assert len(tip.variabili) == 0
    assert len(tip.elementi) == 0
    
    # Aggiungi variabile
    tip.variabili.append(VariabileRilievo("L", "Larghezza", True, 1200.0))
    assert len(tip.variabili) == 1
    
    # Test serializzazione/deserializzazione
    data = tip.to_dict()
    tip2 = TipologiaInfisso.from_dict(data)
    assert tip2.nome == tip.nome
    assert len(tip2.variabili) == 1


def test_menu_item():
    """Test MenuItem"""
    menu = MenuItem(
        id="home",
        nome="Home",
        icona="mdi:home",
        colore="#00ff88",
        ordine=0
    )
    
    assert menu.id == "home"
    assert menu.azione == "navigate"
    assert len(menu.figli) == 0
    
    # Aggiungi sottomenu
    submenu = MenuItem(
        id="home_sub",
        nome="Submenu",
        icona="mdi:arrow-right"
    )
    menu.figli.append(submenu)
    assert len(menu.figli) == 1
    
    # Test serializzazione/deserializzazione
    data = menu.to_dict()
    menu2 = MenuItem.from_dict(data)
    assert menu2.nome == menu.nome
    assert len(menu2.figli) == 1


def test_astina_config():
    """Test AstinaConfig"""
    astina = AstinaConfig(
        id="ant_rib_inf",
        nome="Inferiore AR",
        gruppo="Anta Ribalta",
        offset=-3.0,
        colore="#9d4edd"
    )
    
    assert astina.gruppo == "Anta Ribalta"
    assert astina.offset == -3.0
    assert astina.attivo is True
    
    # Test serializzazione/deserializzazione
    data = astina.to_dict()
    astina2 = AstinaConfig.from_dict(data)
    assert astina2.nome == astina.nome


def test_fermavetro_config():
    """Test FermavetroConfig"""
    fv = FermavetroConfig(
        id="fv_alluminio",
        nome="Fermavetro Alluminio",
        materiale="Alluminio",
        offset=-12.0
    )
    
    assert fv.materiale == "Alluminio"
    assert fv.offset == -12.0
    
    # Test serializzazione/deserializzazione
    data = fv.to_dict()
    fv2 = FermavetroConfig.from_dict(data)
    assert fv2.materiale == fv.materiale


def test_progetto_configurazione():
    """Test ProgettoConfigurazione"""
    progetto = ProgettoConfigurazione(
        nome="Test Project",
        version="1.0.0"
    )
    
    assert progetto.nome == "Test Project"
    assert progetto.version == "1.0.0"
    assert len(progetto.menus) == 0
    assert len(progetto.tipologie) == 0
    
    # Aggiungi elementi
    progetto.menus.append(MenuItem("home", "Home", "mdi:home"))
    progetto.tipologie.append(TipologiaInfisso("tip1", "Tip1", "icon1"))
    
    # Test serializzazione/deserializzazione
    data = progetto.to_dict()
    assert "nome" in data
    assert "menus" in data
    
    progetto2 = ProgettoConfigurazione.from_dict(data)
    assert progetto2.nome == progetto.nome
    assert len(progetto2.menus) == 1
    assert len(progetto2.tipologie) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

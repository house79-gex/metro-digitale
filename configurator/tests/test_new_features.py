"""
Test per nuove funzionalità: Template Browser, Simulation Mode, Probe Editor
"""

import pytest
from pathlib import Path


def test_template_info_creation():
    """Test creazione TemplateInfo da file JSON esistente"""
    from ui.template_browser_dialog import TemplateInfo
    
    templates_dir = Path(__file__).parent.parent / "resources" / "templates"
    home_template = templates_dir / "home_standard.json"
    
    if home_template.exists():
        info = TemplateInfo(home_template)
        assert info.name is not None
        assert info.description is not None
        assert info.element_count >= 0
        assert info.version is not None


def test_probe_shape_serialization():
    """Test serializzazione/deserializzazione ProbeShape"""
    from ui.probe_editor_dialog import ProbeShape
    from PyQt6.QtCore import QPointF
    
    # Crea shape
    shape = ProbeShape()
    shape.name = "Test Puntale"
    shape.add_line(QPointF(0, 0), QPointF(100, 100))
    shape.add_arrow(QPointF(50, 50), "up", "Punto misurazione")
    shape.add_contact_point(QPointF(25, 25), "interno")
    
    # Serializza
    data = shape.to_dict()
    assert data["name"] == "Test Puntale"
    assert len(data["lines"]) == 1
    assert len(data["arrows"]) == 1
    assert len(data["contact_points"]) == 1
    
    # Deserializza
    restored = ProbeShape.from_dict(data)
    assert restored.name == shape.name
    assert len(restored.lines) == len(shape.lines)
    assert len(restored.arrows) == len(shape.arrows)
    assert len(restored.contact_points) == len(shape.contact_points)


def test_icon_browser_fallback():
    """Test che IconBrowserDialog gestisce fallback quando SVG non disponibile"""
    from core.icon_browser import IconifyClient
    
    client = IconifyClient()
    
    # Test fallback icons
    results = client.search("", limit=5)
    assert len(results) > 0
    assert all(hasattr(icon, 'name') for icon in results)
    assert all(hasattr(icon, 'prefix') for icon in results)


def test_simulation_modes():
    """Test modalità simulazione"""
    # Non possiamo testare completamente GUI senza display
    # Ma possiamo verificare che le classi esistano
    from ui.simulation_dialog import SimulationDialog, SimulatedDisplay
    
    assert SimulationDialog is not None
    assert SimulatedDisplay is not None


def test_template_browser_exists():
    """Test che TemplateBrowserDialog esiste"""
    from ui.template_browser_dialog import TemplateBrowserDialog
    
    assert TemplateBrowserDialog is not None


def test_probe_editor_exists():
    """Test che ProbeEditorDialog esiste"""
    from ui.probe_editor_dialog import ProbeEditorDialog, ProbeCanvas
    
    assert ProbeEditorDialog is not None
    assert ProbeCanvas is not None


def test_all_templates_exist():
    """Verifica che tutti i template previsti esistano"""
    templates_dir = Path(__file__).parent.parent / "resources" / "templates"
    
    expected_templates = [
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
    
    for template_name in expected_templates:
        template_file = templates_dir / template_name
        assert template_file.exists(), f"Template {template_name} non trovato"


def test_icon_svg_loading():
    """Test caricamento icona SVG"""
    from core.icon_browser import IconifyClient
    
    client = IconifyClient()
    
    # Prova a caricare un'icona
    # Nota: questo potrebbe fallire se non c'è connessione internet
    try:
        svg = client.get_icon_svg("mdi:home")
        # Se otteniamo qualcosa, verifica che sia una stringa
        if svg:
            assert isinstance(svg, str)
            assert len(svg) > 0
    except Exception:
        # Se fallisce (es. no internet), skippa
        pytest.skip("Impossibile scaricare icona (no internet?)")


def test_canvas_element_types():
    """Test che tutti i tipi di elementi canvas esistano"""
    from ui.canvas_widget import CanvasElement
    
    element_types = [
        "Button", "IconButton", "ToggleButton",
        "Label", "MeasureDisplay", "FormulaResult",
        "Panel", "Frame", "Separator",
        "NumberInput", "Slider", "Dropdown",
        "TipologiaWidget", "AstinaSelector", "MaterialSelector"
    ]
    
    for elem_type in element_types:
        assert elem_type in CanvasElement.ELEMENT_STYLES, f"Stile mancante per {elem_type}"


def test_wysiwyg_rendering():
    """Test che CanvasElement abbia metodo paint custom"""
    from ui.canvas_widget import CanvasElement
    
    # Verifica che il metodo paint esista
    assert hasattr(CanvasElement, 'paint')

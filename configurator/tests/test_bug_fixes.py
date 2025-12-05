"""
Test per verificare i bug fix: IconBrowser, MainWindow, Canvas, Proprietà
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.icon_browser import IconifyClient


def test_icon_browser_recommended_sets_tuple():
    """Test che RECOMMENDED_SETS sia una lista di tuple"""
    client = IconifyClient()
    
    # Verifica che sia una lista
    assert isinstance(client.RECOMMENDED_SETS, list)
    assert len(client.RECOMMENDED_SETS) > 0
    
    # Verifica che ogni elemento sia una tupla (prefix, name)
    for item in client.RECOMMENDED_SETS:
        assert isinstance(item, tuple)
        assert len(item) == 2
        prefix, name = item
        assert isinstance(prefix, str)
        assert isinstance(name, str)
        assert len(prefix) > 0
        assert len(name) > 0


def test_icon_browser_search_prefix_parameter():
    """Test che search() accetti il parametro 'prefix' corretto"""
    client = IconifyClient()
    
    # Test con prefix=None (dovrebbe funzionare)
    results = client.search("home", limit=5, prefix=None)
    assert isinstance(results, list)
    
    # Test con prefix specifico
    results = client.search("home", limit=5, prefix="mdi")
    assert isinstance(results, list)


def test_display_dimensions_constants():
    """Test che DisplayPreviewWidget abbia le costanti corrette"""
    # Verifica leggendo il file invece di importare PyQt6
    import re
    with open('ui/canvas_widget.py', 'r') as f:
        content = f.read()
    
    # Cerca le costanti
    width_match = re.search(r'DISPLAY_WIDTH\s*=\s*(\d+)', content)
    height_match = re.search(r'DISPLAY_HEIGHT\s*=\s*(\d+)', content)
    
    assert width_match is not None, "DISPLAY_WIDTH not found"
    assert height_match is not None, "DISPLAY_HEIGHT not found"
    
    assert int(width_match.group(1)) == 800
    assert int(height_match.group(1)) == 480


def test_canvas_element_accepts_canvas_widget():
    """Test che CanvasElement accetti il parametro canvas_widget"""
    # Verifica leggendo il file
    import re
    with open('ui/canvas_widget.py', 'r') as f:
        content = f.read()
    
    # Cerca la definizione del costruttore di CanvasElement
    pattern = r'def __init__\(self,\s*element_type:.*?canvas_widget.*?\):'
    assert re.search(pattern, content) is not None


def test_canvas_widget_has_properties_signal():
    """Test che CanvasWidget abbia il segnale open_properties_requested"""
    # Verifica leggendo il file
    with open('ui/canvas_widget.py', 'r') as f:
        content = f.read()
    
    assert 'open_properties_requested = pyqtSignal(object)' in content


if __name__ == "__main__":
    print("Running bug fix tests...")
    
    test_icon_browser_recommended_sets_tuple()
    print("✓ test_icon_browser_recommended_sets_tuple")
    
    test_icon_browser_search_prefix_parameter()
    print("✓ test_icon_browser_search_prefix_parameter")
    
    test_display_dimensions_constants()
    print("✓ test_display_dimensions_constants")
    
    test_canvas_element_accepts_canvas_widget()
    print("✓ test_canvas_element_accepts_canvas_widget")
    
    test_canvas_widget_has_properties_signal()
    print("✓ test_canvas_widget_has_properties_signal")
    
    print("\n✓ All bug fix tests passed!")

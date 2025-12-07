"""
Test per verificare i fix dei TypeError float/int in QPainter
Verifica che tutte le coordinate passate a drawLine e drawText siano int
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_canvas_widget_drawline_int_coords():
    """Test che canvas_widget.py usi int() per tutte le coordinate drawLine"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'canvas_widget.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica che le linee 124-127 siano convertite a int
    # Cerca il pattern specifico del fix per Button
    button_section = re.search(
        r'elif "Button" in self\.element_type:.*?painter\.drawLine\(int\(rect\.left\(\) \+ 2\)',
        content,
        re.DOTALL
    )
    assert button_section is not None, "Button drawLine non usa int() per le coordinate"
    
    # Verifica che la linea per Slider sia corretta
    slider_section = re.search(
        r'painter\.drawLine\(10, int\(mid_y\), int\(rect\.width\(\) - 10\), int\(mid_y\)\)',
        content
    )
    assert slider_section is not None, "Slider drawLine non usa int() correttamente"


def test_probe_editor_drawtext_int_coords():
    """Test che probe_editor_dialog.py usi int() per tutte le coordinate drawText"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Trova tutte le chiamate a drawText
    drawtext_calls = re.findall(r'painter\.drawText\([^)]+\)', content)
    
    # Verifica che ci siano chiamate a drawText
    assert len(drawtext_calls) > 0, "Nessuna chiamata drawText trovata"
    
    # Verifica che le coordinate numeriche siano int
    # Le chiamate drawText con coordinate numeriche dovrebbero avere int()
    for call in drawtext_calls:
        # Se contiene coordinate numeriche dirette (non QRect), devono essere int()
        if re.search(r',\s*\d+\s*,', call):
            # Skippa le chiamate con QRect che hanno AlignmentFlag
            if 'Qt.AlignmentFlag' in call or 'AlignCenter' in call:
                continue
            # Verifica che ci sia int() prima delle coordinate
            assert 'int(' in call, f"drawText senza int() trovato: {call}"


def test_template_browser_qicon_wrapper():
    """Test che template_browser_dialog.py usi QIcon() per wrappare QPixmap"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'template_browser_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica che ci sia il pattern: item.setIcon(QIcon(thumbnail))
    pattern = r'item\.setIcon\(QIcon\(thumbnail\)\)'
    assert re.search(pattern, content) is not None, "QIcon wrapper non trovato per thumbnail"
    
    # Verifica che QIcon sia importato
    assert 'from PyQt6.QtGui import' in content and 'QIcon' in content, "QIcon non importato"


def test_tooltip_manager_hasattr_check():
    """Test che tooltip_manager.py usi hasattr prima di setToolTipDuration"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'tooltip_manager.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica che ci sia il controllo hasattr prima di setToolTipDuration
    pattern = r'if hasattr\(widget, [\'"]setToolTipDuration[\'"]\):.*?widget\.setToolTipDuration'
    assert re.search(pattern, content, re.DOTALL) is not None, \
        "hasattr check per setToolTipDuration non trovato"


def test_icon_browser_search_limit():
    """Test che icon_browser_dialog.py abbia un limite di ricerca >= 99"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'icon_browser_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Cerca il limite nella chiamata search
    limit_match = re.search(r'client\.search\([^,]+,\s*limit=(\d+)', content)
    assert limit_match is not None, "Parametro limit non trovato in search()"
    
    limit_value = int(limit_match.group(1))
    assert limit_value >= 99, f"Limite di ricerca troppo basso: {limit_value} (deve essere >= 99)"


def test_probe_editor_canvas_initialization_order():
    """Test che probe_editor_dialog.py crei canvas prima di toolbar"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Trova le posizioni di creazione canvas e toolbar
    canvas_pos = content.find('self.canvas = ProbeCanvas()')
    toolbar_pos = content.find('toolbar = self._create_toolbar()')
    
    assert canvas_pos != -1, "Creazione canvas non trovata"
    assert toolbar_pos != -1, "Creazione toolbar non trovata"
    assert canvas_pos < toolbar_pos, "Canvas deve essere creato prima di toolbar"


if __name__ == "__main__":
    print("Running TypeError fix tests...")
    
    test_canvas_widget_drawline_int_coords()
    print("✓ test_canvas_widget_drawline_int_coords")
    
    test_probe_editor_drawtext_int_coords()
    print("✓ test_probe_editor_drawtext_int_coords")
    
    test_template_browser_qicon_wrapper()
    print("✓ test_template_browser_qicon_wrapper")
    
    test_tooltip_manager_hasattr_check()
    print("✓ test_tooltip_manager_hasattr_check")
    
    test_icon_browser_search_limit()
    print("✓ test_icon_browser_search_limit")
    
    test_probe_editor_canvas_initialization_order()
    print("✓ test_probe_editor_canvas_initialization_order")
    
    print("\n✓ All TypeError fix tests passed!")

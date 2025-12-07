"""
Test per verificare le correzioni critiche degli errori
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_probe_editor_drawtext_int_conversion():
    """Test che drawText in probe_editor_dialog.py usi coordinate int"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Cerca tutte le chiamate drawText per verificare che usino int()
    # Linea 158: painter.drawText(int(center_x + 5), 15, "Y")
    assert 'painter.drawText(int(center_x + 5), 15, "Y")' in content, "Line 158 should use int()"
    
    # Linea 159: painter.drawText(int(self.width() - 15), int(center_y - 5), "X")
    assert 'painter.drawText(int(self.width() - 15), int(center_y - 5), "X")' in content, "Line 159 should use int()"
    
    # Linea 233: painter.drawText(int(end.x() + 10), int(end.y() - 10), label)
    assert 'painter.drawText(int(end.x() + 10), int(end.y() - 10), label)' in content, "Line 233 should use int()"
    
    # Linea 255: painter.drawText(int(pos.x() - 10), int(pos.y() + 4), label)
    assert 'painter.drawText(int(pos.x() - 10), int(pos.y() + 4), label)' in content, "Line 255 should use int()"
    
    # Linea 261: painter.drawText(int(pos.x() - 40), int(pos.y() + 25), text)
    assert 'painter.drawText(int(pos.x() - 40), int(pos.y() + 25), text)' in content, "Line 261 should use int()"


def test_template_browser_qicon_fix():
    """Test che template_browser_dialog.py usi QIcon invece di QPixmap direttamente"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'template_browser_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica che QIcon sia importato
    assert 'from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon' in content, "QIcon should be imported"
    
    # Verifica che setIcon usi QIcon
    assert 'item.setIcon(QIcon(thumbnail))' in content, "setIcon should use QIcon(thumbnail)"


def test_canvas_widget_drawline_int_conversion():
    """Test che drawLine in canvas_widget.py usi coordinate int"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'canvas_widget.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Linea 145: painter.drawLine(10, int(mid_y), int(rect.width() - 10), int(mid_y))
    assert 'painter.drawLine(10, int(mid_y), int(rect.width() - 10), int(mid_y))' in content, "Line 145 should use int()"


def test_tooltip_manager_hasattr_check():
    """Test che tooltip_manager.py usi hasattr per setToolTipDuration"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'tooltip_manager.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica che ci siano controlli hasattr per setToolTipDuration
    assert content.count("if hasattr(widget, 'setToolTipDuration'):") >= 2, "Should have hasattr checks for setToolTipDuration"


def test_icon_browser_increased_limit():
    """Test che icon_browser_dialog.py usi limite aumentato per le icone"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'icon_browser_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica che il limite sia aumentato a 100
    assert 'limit=100' in content, "Icon search limit should be increased to 100"


def test_probe_editor_canvas_init_order():
    """Test che canvas sia creato prima della toolbar in probe_editor_dialog.py"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    canvas_line = None
    toolbar_line = None
    
    for i, line in enumerate(lines):
        if 'self.canvas = ProbeCanvas()' in line:
            canvas_line = i
        elif 'toolbar = self._create_toolbar()' in line:
            toolbar_line = i
    
    assert canvas_line is not None, "self.canvas = ProbeCanvas() should exist"
    assert toolbar_line is not None, "toolbar = self._create_toolbar() should exist"
    assert canvas_line < toolbar_line, "canvas should be created before toolbar"


if __name__ == "__main__":
    print("Running critical fix tests...")
    
    test_probe_editor_drawtext_int_conversion()
    print("✓ test_probe_editor_drawtext_int_conversion")
    
    test_template_browser_qicon_fix()
    print("✓ test_template_browser_qicon_fix")
    
    test_canvas_widget_drawline_int_conversion()
    print("✓ test_canvas_widget_drawline_int_conversion")
    
    test_tooltip_manager_hasattr_check()
    print("✓ test_tooltip_manager_hasattr_check")
    
    test_icon_browser_increased_limit()
    print("✓ test_icon_browser_increased_limit")
    
    test_probe_editor_canvas_init_order()
    print("✓ test_probe_editor_canvas_init_order")
    
    print("\n✓ All critical fix tests passed!")

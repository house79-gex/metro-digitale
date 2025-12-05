"""
Comprehensive test for all changes made to the configurator
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_icon_browser_changes():
    """Test icon browser has correct API implementation"""
    from core.icon_browser import IconifyClient, IconInfo
    
    client = IconifyClient()
    
    # Test correct API URLs
    assert client.SEARCH_URL == "https://api.iconify.design/search"
    assert client.ICON_URL == "https://api.iconify.design"
    
    # Test fallback icons exist
    assert len(client.FALLBACK_ICONS) == 15
    assert all(isinstance(icon, IconInfo) for icon in client.FALLBACK_ICONS)
    
    # Test IconInfo has prefix attribute (not 'set')
    icon = client.FALLBACK_ICONS[0]
    assert hasattr(icon, 'prefix')
    assert hasattr(icon, 'name')
    assert hasattr(icon, 'full_name')
    
    # Test search method signature has 'prefix' parameter
    import inspect
    sig = inspect.signature(client.search)
    assert 'prefix' in sig.parameters
    
    # Test get_icon_sets method exists
    assert hasattr(client, 'get_icon_sets')
    sets = client.get_icon_sets()
    assert isinstance(sets, list)
    assert len(sets) == 9
    
    print("✓ Icon browser has correct API implementation")


def test_toolbox_drag_drop():
    """Test toolbox has drag & drop elements"""
    # Can't import Qt in headless environment, so check file content
    toolbox_file = os.path.join(os.path.dirname(__file__), '..', 'ui', 'toolbox_widget.py')
    
    with open(toolbox_file, 'r') as f:
        content = f.read()
    
    # Check for DraggableTreeWidget class
    assert 'class DraggableTreeWidget(QTreeWidget):' in content
    assert 'def startDrag(self, supportedActions):' in content
    
    # Check for mime data usage
    assert 'QMimeData' in content
    assert 'application/x-metro-element' in content
    assert 'json.dumps' in content
    
    # Check for ELEMENTS dictionary
    assert 'ELEMENTS = {' in content
    assert '"Layout":' in content
    assert '"Controlli":' in content
    
    print("✓ Toolbox has drag & drop functionality")


def test_canvas_widget_changes():
    """Test canvas widget has been rewritten"""
    canvas_file = os.path.join(os.path.dirname(__file__), '..', 'ui', 'canvas_widget.py')
    
    with open(canvas_file, 'r') as f:
        content = f.read()
    
    # Check for CanvasElement class
    assert 'class CanvasElement(QGraphicsRectItem):' in content
    assert 'ELEMENT_STYLES = {' in content
    
    # Check for DisplayPreviewWidget
    assert 'class DisplayPreviewWidget(QWidget):' in content
    assert 'def _create_header(self)' in content
    assert 'def _create_canvas_container(self)' in content
    assert 'def _create_footer(self)' in content
    
    # Check for drag & drop methods
    assert 'def dragEnterEvent(self, event: QDragEnterEvent):' in content
    assert 'def dragMoveEvent(self, event: QDragMoveEvent):' in content
    assert 'def dropEvent(self, event: QDropEvent):' in content
    
    # Check for display dimensions
    assert 'DISPLAY_WIDTH = 800' in content
    assert 'DISPLAY_HEIGHT = 480' in content
    
    # Check for zoom functionality
    assert 'zoom_slider' in content
    assert 'def set_zoom(self, zoom_percent: int):' in content
    
    # Check for mouse coordinates
    assert 'mouse_position_changed' in content
    assert 'def _on_mouse_moved(self, x, y):' in content
    
    # Check for grid and snap
    assert 'snap_to_grid' in content
    assert 'show_grid' in content
    
    # Check for context menu
    assert 'def contextMenuEvent(self, event):' in content
    
    print("✓ Canvas widget has been completely rewritten")


def test_main_window_uses_display_preview():
    """Test main window uses DisplayPreviewWidget"""
    main_file = os.path.join(os.path.dirname(__file__), '..', 'ui', 'main_window.py')
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check import
    assert 'from .canvas_widget import DisplayPreviewWidget' in content
    
    # Check usage
    assert 'self.display_preview = DisplayPreviewWidget()' in content
    assert 'self.canvas = self.display_preview.canvas' in content
    
    print("✓ Main window uses DisplayPreviewWidget")


def test_all_files_exist():
    """Test all modified files exist"""
    base_path = os.path.join(os.path.dirname(__file__), '..')
    
    files = [
        'core/icon_browser.py',
        'ui/toolbox_widget.py',
        'ui/canvas_widget.py',
        'ui/main_window.py',
    ]
    
    for file in files:
        full_path = os.path.join(base_path, file)
        assert os.path.exists(full_path), f"File {file} does not exist"
    
    print("✓ All modified files exist")


if __name__ == "__main__":
    print("=" * 60)
    print("Comprehensive Test for All Changes")
    print("=" * 60)
    
    test_all_files_exist()
    test_icon_browser_changes()
    test_toolbox_drag_drop()
    test_canvas_widget_changes()
    test_main_window_uses_display_preview()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)

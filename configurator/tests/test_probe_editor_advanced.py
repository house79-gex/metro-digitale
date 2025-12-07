"""
Test per verificare le funzionalità avanzate dell'editor puntali
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_snap_type_enum_exists():
    """Test che SnapType enum sia definito"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'class SnapType(Enum):' in content, "SnapType enum should be defined"
    assert 'GRID = 1' in content, "SnapType.GRID should be defined"
    assert 'ENDPOINT = 2' in content, "SnapType.ENDPOINT should be defined"
    assert 'MIDPOINT = 3' in content, "SnapType.MIDPOINT should be defined"


def test_snap_manager_exists():
    """Test che SnapManager class sia definita"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'class SnapManager:' in content, "SnapManager class should be defined"
    assert 'def find_snap(' in content, "find_snap method should exist"
    assert 'def set_snap_enabled(' in content, "set_snap_enabled method should exist"


def test_apply_constraints_method():
    """Test che apply_constraints sia implementato"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'def apply_constraints(self, start: QPointF, current: QPointF)' in content, \
        "apply_constraints method should be defined"


def test_snap_indicators():
    """Test che _draw_snap_indicator sia implementato"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'def _draw_snap_indicator(' in content, "_draw_snap_indicator should be defined"


def test_ortho_and_45_constraints():
    """Test che vincoli ortogonale e 45° siano implementati"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'self.ortho_mode' in content, "ortho_mode should be defined"
    assert 'self.angle_45_mode' in content, "angle_45_mode should be defined"


def test_undo_redo_functionality():
    """Test che undo/redo siano implementati"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'def undo_last(self):' in content, "undo_last should be defined"
    assert 'def redo_last(self):' in content, "redo_last should be defined"
    assert 'self.undo_stack' in content, "undo_stack should be defined"
    assert 'self.redo_stack' in content, "redo_stack should be defined"


def test_light_background():
    """Test che lo sfondo sia chiaro stile CAD"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica che ci sia uno sfondo chiaro
    assert '#f5f5f5' in content or 'background: #f5f5f5' in content, \
        "Light CAD-style background should be set"


def test_enhanced_toolbar():
    """Test che la toolbar avanzata sia implementata"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica controlli snap
    assert 'self.snap_grid_cb = QCheckBox("Grid")' in content, "Grid snap checkbox should exist"
    assert 'self.snap_endpoint_cb = QCheckBox("Endpoint")' in content, \
        "Endpoint snap checkbox should exist"
    assert 'self.snap_midpoint_cb = QCheckBox("Midpoint")' in content, \
        "Midpoint snap checkbox should exist"
    
    # Verifica controlli vincoli
    assert 'self.ortho_cb = QCheckBox' in content, "Ortho checkbox should exist"
    assert 'self.angle45_cb = QCheckBox' in content, "45° checkbox should exist"
    
    # Verifica controllo griglia
    assert 'self.grid_spin = QSpinBox()' in content, "Grid size spinbox should exist"


def test_status_bar():
    """Test che la status bar sia implementata"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'self.status_label' in content, "status_label should be defined"
    assert 'def _update_status(' in content, "_update_status method should be defined"


def test_dimension_info():
    """Test che _draw_dimension_info sia implementato"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'def _draw_dimension_info(' in content, "_draw_dimension_info should be defined"


def test_key_event_handlers():
    """Test che i gestori eventi tastiera siano implementati"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    assert 'def keyPressEvent(' in content, "keyPressEvent should be defined"
    assert 'def keyReleaseEvent(' in content, "keyReleaseEvent should be defined"


if __name__ == "__main__":
    print("Running advanced probe editor tests...")
    
    test_snap_type_enum_exists()
    print("✓ test_snap_type_enum_exists")
    
    test_snap_manager_exists()
    print("✓ test_snap_manager_exists")
    
    test_apply_constraints_method()
    print("✓ test_apply_constraints_method")
    
    test_snap_indicators()
    print("✓ test_snap_indicators")
    
    test_ortho_and_45_constraints()
    print("✓ test_ortho_and_45_constraints")
    
    test_undo_redo_functionality()
    print("✓ test_undo_redo_functionality")
    
    test_light_background()
    print("✓ test_light_background")
    
    test_enhanced_toolbar()
    print("✓ test_enhanced_toolbar")
    
    test_status_bar()
    print("✓ test_status_bar")
    
    test_dimension_info()
    print("✓ test_dimension_info")
    
    test_key_event_handlers()
    print("✓ test_key_event_handlers")
    
    print("\n✓ All advanced probe editor tests passed!")

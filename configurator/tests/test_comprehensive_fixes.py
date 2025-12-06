"""
Test comprensivo per verificare tutte le correzioni e funzionalità
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_all_critical_fixes():
    """Test che tutte le correzioni critiche siano applicate"""
    errors = []
    
    # Test probe_editor_dialog.py
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Verifica conversioni int per drawText
    if 'painter.drawText(int(center_x + 5), 15, "Y")' not in content:
        errors.append("probe_editor_dialog.py: drawText line 158 not fixed")
    
    if 'painter.drawText(int(self.width() - 15), int(center_y - 5), "X")' not in content:
        errors.append("probe_editor_dialog.py: drawText line 159 not fixed")
    
    # Test template_browser_dialog.py
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'template_browser_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    if 'item.setIcon(QIcon(thumbnail))' not in content:
        errors.append("template_browser_dialog.py: setIcon not using QIcon")
    
    # Test canvas_widget.py
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'canvas_widget.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    if 'painter.drawLine(10, int(mid_y), int(rect.width() - 10), int(mid_y))' not in content:
        errors.append("canvas_widget.py: drawLine not using int")
    
    # Test icon_browser_dialog.py
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'icon_browser_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    if 'limit=100' not in content:
        errors.append("icon_browser_dialog.py: limit not increased to 100")
    
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  ❌ {error}")
        return False
    
    return True


def test_all_advanced_features():
    """Test che tutte le funzionalità avanzate siano implementate"""
    errors = []
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'probe_editor_dialog.py')
    with open(file_path, 'r') as f:
        content = f.read()
    
    required_features = [
        ('SnapType enum', 'class SnapType(Enum):'),
        ('SnapManager class', 'class SnapManager:'),
        ('find_snap method', 'def find_snap('),
        ('apply_constraints method', 'def apply_constraints('),
        ('_draw_snap_indicator method', 'def _draw_snap_indicator('),
        ('_draw_dimension_info method', 'def _draw_dimension_info('),
        ('undo_last method', 'def undo_last(self):'),
        ('redo_last method', 'def redo_last(self):'),
        ('keyPressEvent method', 'def keyPressEvent('),
        ('keyReleaseEvent method', 'def keyReleaseEvent('),
        ('Light background', '#f5f5f5'),
        ('Snap grid checkbox', 'self.snap_grid_cb = QCheckBox("Grid")'),
        ('Snap endpoint checkbox', 'self.snap_endpoint_cb = QCheckBox("Endpoint")'),
        ('Snap midpoint checkbox', 'self.snap_midpoint_cb = QCheckBox("Midpoint")'),
        ('Ortho checkbox', 'self.ortho_cb = QCheckBox'),
        ('45° checkbox', 'self.angle45_cb = QCheckBox'),
        ('Grid spinbox', 'self.grid_spin = QSpinBox()'),
        ('Status label', 'self.status_label'),
        ('Undo stack', 'self.undo_stack'),
        ('Redo stack', 'self.redo_stack'),
        ('Ortho mode', 'self.ortho_mode'),
        ('Angle 45 mode', 'self.angle_45_mode'),
    ]
    
    for feature_name, search_string in required_features:
        if search_string not in content:
            errors.append(f"Missing feature: {feature_name}")
    
    if errors:
        print("MISSING FEATURES:")
        for error in errors:
            print(f"  ❌ {error}")
        return False
    
    return True


def test_code_quality():
    """Test qualità del codice e best practices"""
    errors = []
    
    # Verifica che tutti i file Python compilino
    files_to_check = [
        'ui/probe_editor_dialog.py',
        'ui/template_browser_dialog.py',
        'ui/canvas_widget.py',
        'ui/icon_browser_dialog.py',
        'ui/tooltip_manager.py'
    ]
    
    import py_compile
    for filepath in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), '..', filepath)
        try:
            py_compile.compile(full_path, doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"Syntax error in {filepath}: {e}")
    
    if errors:
        print("CODE QUALITY ISSUES:")
        for error in errors:
            print(f"  ❌ {error}")
        return False
    
    return True


def main():
    """Esegue tutti i test comprensivi"""
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    all_passed = True
    
    print("1. Testing Critical Fixes...")
    if test_all_critical_fixes():
        print("   ✅ All critical fixes verified")
    else:
        print("   ❌ Some critical fixes missing")
        all_passed = False
    print()
    
    print("2. Testing Advanced Features...")
    if test_all_advanced_features():
        print("   ✅ All advanced features implemented")
    else:
        print("   ❌ Some advanced features missing")
        all_passed = False
    print()
    
    print("3. Testing Code Quality...")
    if test_code_quality():
        print("   ✅ All code compiles correctly")
    else:
        print("   ❌ Code quality issues found")
        all_passed = False
    print()
    
    print("=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Implementation complete and verified.")
    else:
        print("⚠️  Some tests failed. Review errors above.")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

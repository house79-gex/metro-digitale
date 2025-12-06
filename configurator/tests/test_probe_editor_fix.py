"""
Test per fix ProbeEditorDialog - verifica che canvas sia accessibile da toolbar
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_probe_editor_canvas_before_toolbar():
    """Test che il canvas sia creato prima della toolbar"""
    # Questo test verifica che l'ordine di inizializzazione sia corretto
    # leggendo il codice sorgente del file
    
    from pathlib import Path
    
    probe_editor_file = Path(__file__).parent.parent / "ui" / "probe_editor_dialog.py"
    assert probe_editor_file.exists(), "probe_editor_dialog.py not found"
    
    with open(probe_editor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova la posizione della creazione del canvas
    canvas_creation = content.find('self.canvas = ProbeCanvas()')
    assert canvas_creation > 0, "Canvas creation not found"
    
    # Trova la posizione della creazione della toolbar
    toolbar_creation = content.find('toolbar = self._create_toolbar()')
    assert toolbar_creation > 0, "Toolbar creation not found"
    
    # Verifica che il canvas sia creato PRIMA della toolbar
    assert canvas_creation < toolbar_creation, \
        "Canvas deve essere creato PRIMA della toolbar per evitare AttributeError"
    
    print(f"✓ Canvas creation at position {canvas_creation}")
    print(f"✓ Toolbar creation at position {toolbar_creation}")
    print("✓ Canvas is correctly created before toolbar")


def test_tooltip_manager_hasattr_check():
    """Test che tooltip_manager controlli hasattr prima di setToolTipDuration"""
    from pathlib import Path
    
    tooltip_manager_file = Path(__file__).parent.parent / "ui" / "tooltip_manager.py"
    assert tooltip_manager_file.exists(), "tooltip_manager.py not found"
    
    with open(tooltip_manager_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica che ci sia un controllo hasattr prima di setToolTipDuration
    assert "hasattr(widget, 'setToolTipDuration')" in content, \
        "Missing hasattr check before setToolTipDuration"
    
    # Verifica che tutti gli usi di setToolTipDuration siano protetti
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Ignora commenti e righe vuote
        stripped = line.strip()
        if stripped.startswith('#') or not stripped:
            continue
        
        if 'setToolTipDuration' in line and 'hasattr' not in line:
            # Verifica che la riga precedente contenga hasattr
            if i > 0:
                prev_line = lines[i-1].strip()
                # Cerca hasattr nelle righe precedenti (massimo 3 righe indietro)
                found_hasattr = False
                for j in range(max(0, i-3), i+1):
                    if 'hasattr' in lines[j]:
                        found_hasattr = True
                        break
                assert found_hasattr, \
                    f"Unprotected setToolTipDuration at line {i+1}: {line}"
    
    print("✓ All setToolTipDuration calls are protected with hasattr check")


def test_canvas_methods_exist():
    """Test che i metodi del canvas esistano e siano accessibili"""
    from pathlib import Path
    
    probe_editor_file = Path(__file__).parent.parent / "ui" / "probe_editor_dialog.py"
    
    with open(probe_editor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica che ProbeCanvas abbia i metodi undo_last e clear
    assert 'def undo_last(self):' in content, "ProbeCanvas.undo_last method not found"
    assert 'def clear(self):' in content, "ProbeCanvas.clear method not found"
    
    # Verifica che la toolbar chiami questi metodi
    assert 'self.canvas.undo_last' in content, "Toolbar doesn't call canvas.undo_last"
    assert 'self.canvas.clear' in content or 'self._clear_canvas' in content, \
        "Toolbar doesn't call canvas.clear"
    
    print("✓ Canvas methods undo_last and clear exist")
    print("✓ Toolbar correctly references canvas methods")


if __name__ == "__main__":
    print("Running ProbeEditor fix tests...\n")
    
    test_probe_editor_canvas_before_toolbar()
    print()
    
    test_tooltip_manager_hasattr_check()
    print()
    
    test_canvas_methods_exist()
    print()
    
    print("✓ All ProbeEditor fix tests passed!")

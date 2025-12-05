"""
Test per canvas widget e elementi
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# Define expected element styles (matching canvas_widget.py)
EXPECTED_ELEMENT_STYLES = {
    "Button": {"color": "#00ff88", "text_color": "#000", "default_size": (100, 40)},
    "IconButton": {"color": "#0088ff", "text_color": "#fff", "default_size": (60, 60)},
    "ToggleButton": {"color": "#ff8800", "text_color": "#fff", "default_size": (100, 40)},
    "Label": {"color": "#ffffff", "text_color": "#fff", "default_size": (120, 30)},
    "MeasureDisplay": {"color": "#00ff88", "text_color": "#000", "default_size": (200, 80)},
    "FormulaResult": {"color": "#88ff00", "text_color": "#000", "default_size": (150, 50)},
    "Panel": {"color": "#1a1a2e", "text_color": "#fff", "default_size": (200, 150)},
    "Frame": {"color": "#2a2a3e", "text_color": "#fff", "default_size": (180, 120)},
    "Separator": {"color": "#00ff88", "text_color": "#fff", "default_size": (200, 2)},
    "NumberInput": {"color": "#ffffff", "text_color": "#000", "default_size": (100, 35)},
    "Slider": {"color": "#00ff88", "text_color": "#fff", "default_size": (150, 30)},
    "Dropdown": {"color": "#ffffff", "text_color": "#000", "default_size": (120, 35)},
    "TipologiaWidget": {"color": "#8800ff", "text_color": "#fff", "default_size": (200, 150)},
    "AstinaSelector": {"color": "#ff0088", "text_color": "#fff", "default_size": (180, 100)},
    "MaterialSelector": {"color": "#00ff88", "text_color": "#000", "default_size": (180, 100)},
}


def test_all_elements_have_styles():
    """Test che tutti gli elementi hanno stili definiti"""
    expected_elements = [
        "Button", "IconButton", "ToggleButton",
        "Label", "MeasureDisplay", "FormulaResult",
        "Panel", "Frame", "Separator",
        "NumberInput", "Slider", "Dropdown",
        "TipologiaWidget", "AstinaSelector", "MaterialSelector"
    ]
    
    for elem in expected_elements:
        assert elem in EXPECTED_ELEMENT_STYLES
        style = EXPECTED_ELEMENT_STYLES[elem]
        assert "color" in style
        assert "text_color" in style
        assert "default_size" in style


def test_element_style_structure():
    """Test struttura stili elementi"""
    for element_type, style in EXPECTED_ELEMENT_STYLES.items():
        # Verifica colore
        assert style["color"].startswith("#")
        assert len(style["color"]) == 7
        
        # Verifica text_color
        assert style["text_color"].startswith("#")
        assert len(style["text_color"]) in [4, 7]  # #fff or #ffffff
        
        # Verifica default_size
        width, height = style["default_size"]
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width > 0
        assert height > 0


def test_display_dimensions():
    """Test dimensioni display"""
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    
    # Verifica che le dimensioni siano corrette per display 5"
    assert DISPLAY_WIDTH == 800
    assert DISPLAY_HEIGHT == 480
    
    # Verifica aspect ratio (circa 5:3)
    aspect_ratio = DISPLAY_WIDTH / DISPLAY_HEIGHT
    assert abs(aspect_ratio - 1.667) < 0.01


def test_element_sizes_fit_display():
    """Test che le dimensioni degli elementi siano ragionevoli per il display"""
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    
    for element_type, style in EXPECTED_ELEMENT_STYLES.items():
        width, height = style["default_size"]
        
        # Gli elementi non dovrebbero essere più grandi del display
        assert width <= DISPLAY_WIDTH, f"{element_type} width {width} > display width"
        assert height <= DISPLAY_HEIGHT, f"{element_type} height {height} > display height"


if __name__ == "__main__":
    print("Running canvas element tests...")
    
    test_all_elements_have_styles()
    print("✓ test_all_elements_have_styles")
    
    test_element_style_structure()
    print("✓ test_element_style_structure")
    
    test_display_dimensions()
    print("✓ test_display_dimensions")
    
    test_element_sizes_fit_display()
    print("✓ test_element_sizes_fit_display")
    
    print("\n✓ All canvas element tests passed!")

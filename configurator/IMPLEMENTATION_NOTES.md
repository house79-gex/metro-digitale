# Implementation Notes: Canvas with 5" Display + Drag & Drop + Icon Browser

## Overview

This implementation addresses three main improvements to the Metro Digitale Configurator:

1. **Icon Browser with Working Iconify API**
2. **Drag & Drop from Toolbox to Canvas**
3. **5" Display Canvas with Real Proportions and Instrument Frame**

## 1. Icon Browser (`configurator/core/icon_browser.py`)

### Changes Made

- **Correct API Endpoint**: Changed from invalid endpoint to `https://api.iconify.design/search`
- **Search Method**: Updated to use proper Iconify search API with query parameters
- **Fallback Icons**: Added 15 common icons for offline mode
- **Error Handling**: Added timeout (10 seconds) and exception handling
- **Cache System**: SVG files are cached locally in `~/.metro_digitale/icons`

### Key Features

```python
# Search with fallback
results = client.search("home", limit=64)
# Returns IconInfo objects with prefix:name format (e.g., "mdi:home")

# Get SVG with color and size
svg = client.get_svg("mdi:home", color="#ffffff", size=24)

# Fallback icons (15 common icons)
client.FALLBACK_ICONS  # Available offline
```

### API Structure

- **IconInfo**: Changed from `set` attribute to `prefix` attribute (matching Iconify API)
- **Search Response**: Parses icon names in format `prefix:name` from API response
- **Fallback Search**: Searches within fallback icons when API is unavailable

## 2. Toolbox Widget (`configurator/ui/toolbox_widget.py`)

### Changes Made

- **DraggableTreeWidget Class**: Custom QTreeWidget with drag support
- **startDrag() Method**: Implements drag operation with MIME data
- **MIME Format**: Uses `application/x-metro-element` with JSON payload
- **Element Definitions**: 15 elements across 5 categories with icons and descriptions

### Element Categories

1. **Layout**: Panel, Frame, Separator
2. **Testo**: Label, MeasureDisplay, FormulaResult
3. **Controlli**: Button, IconButton, ToggleButton
4. **Input**: NumberInput, Slider, Dropdown
5. **Speciali**: TipologiaWidget, AstinaSelector, MaterialSelector

### Drag & Drop MIME Data

```json
{
  "type": "Button",
  "category": "📁 Controlli"
}
```

### Visual Improvements

- Title with icon: "📦 Elementi"
- Hint text: "Trascina elementi sul canvas →"
- Category folders with 📁 icon
- Element icons for each type (□, ▣, Aa, etc.)
- Tooltips with descriptions

## 3. Canvas Widget (`configurator/ui/canvas_widget.py`)

### Major Rewrite

Complete rewrite to implement:

1. **Realistic 5" Display Visualization**
2. **Drag & Drop Support**
3. **Element Management**
4. **Zoom and Navigation**

### Display Specifications

- **Size**: 800x480 pixels (5" display real proportions)
- **Aspect Ratio**: 5:3 (1.667)
- **Frame**: 3D gradient gray frame simulating instrument case
- **Border**: 3px green (#00ff88) border around display area
- **Dimensions**: Pixel indicators on top and left edges

### CanvasElement Class

```python
class CanvasElement(QGraphicsRectItem):
    ELEMENT_STYLES = {
        "Button": {"color": "#00ff88", "text_color": "#000", "default_size": (100, 40)},
        "Label": {"color": "#ffffff", "text_color": "#fff", "default_size": (120, 30)},
        # ... 15 element types with unique styles
    }
```

### Features

- **Selection**: Orange border (#ff8800) when selected
- **Context Menu**: Right-click for Delete, Duplicate, Properties
- **Snap to Grid**: Optional grid snapping (10px default)
- **Movable**: Drag elements within display area
- **Styled**: Each element type has unique color and default size

### DisplayPreviewWidget Class

Container widget with three sections:

1. **Header**
   - Display info: "📺 Display 5\" (800x480) - Metro Digitale ESP32"
   - Zoom slider (50% - 200%)
   - Current zoom percentage display

2. **Canvas Container**
   - 3D gradient frame (gray with border)
   - Canvas with display area
   - Centered alignment

3. **Footer**
   - Real-time mouse coordinates: "Mouse: (x, y)"
   - Grid and snap status: "Grid: 10px | Snap: ON"

### Drag & Drop Implementation

```python
def dragEnterEvent(self, event):
    # Accept drops from toolbox
    if event.mimeData().hasFormat('application/x-metro-element'):
        event.acceptProposedAction()

def dragMoveEvent(self, event):
    # Validate position is within display bounds
    pos = self.mapToScene(event.position().toPoint())
    if 0 <= pos.x() <= 800 and 0 <= pos.y() <= 480:
        event.acceptProposedAction()

def dropEvent(self, event):
    # Create element at drop position
    data = json.loads(event.mimeData().data('...').data())
    element = CanvasElement(data['type'], x, y)
    self.scene.addItem(element)
```

### Grid System

- **Dotted Grid**: Optional visual grid (10px default)
- **Snap to Grid**: Elements snap to grid when moved/dropped
- **Configurable**: Grid size adjustable from 5px to 50px

## 4. Main Window Updates (`configurator/ui/main_window.py`)

### Changes Made

- Import changed from `CanvasWidget` to `DisplayPreviewWidget`
- Central widget now uses `DisplayPreviewWidget`
- Canvas accessed via `self.display_preview.canvas`

```python
# Before
self.canvas = CanvasWidget()
self.setCentralWidget(self.canvas)

# After
self.display_preview = DisplayPreviewWidget()
self.canvas = self.display_preview.canvas
self.setCentralWidget(self.display_preview)
```

## Testing

### Test Files Created

1. **test_icon_browser_api.py**: Tests IconInfo, search, fallback, SVG download
2. **test_toolbox_drag.py**: Tests element structure, MIME data format
3. **test_canvas_elements.py**: Tests element styles, display dimensions
4. **test_all_changes.py**: Comprehensive test of all modifications

### Test Results

All tests pass successfully:
- Icon browser API implementation verified
- Fallback mechanism working (15 icons available offline)
- Drag & drop MIME data format correct
- All 15 element types have proper styles
- Display dimensions correct for 5" screen
- Element sizes fit within display bounds

## Visual Design

### Color Scheme

- **Primary Green**: #00ff88 (borders, highlights)
- **Dark Blue**: #16213e (display background)
- **Very Dark**: #0f3460 (headers, footers)
- **Orange**: #ff8800 (selection)
- **Gray Gradient**: 3D frame effect

### Typography

- **Headers**: Bold, 14px, Green
- **Body**: Arial, 10-12px
- **Hints**: 11px, Gray
- **Element Labels**: Bold, 10px

### Layout

```
┌─────────────────────────────────────────────────┐
│ Header (Display info + Zoom slider)            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  3D Gray Frame                           │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  Canvas (800x480)                  │  │  │
│  │  │  Green Border                      │  │  │
│  │  │  [Elements appear here]            │  │  │
│  │  └────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
├─────────────────────────────────────────────────┤
│ Footer (Mouse coords + Grid status)            │
└─────────────────────────────────────────────────┘
```

## Usage

### Drag & Drop Workflow

1. Select element from toolbox (left panel)
2. Drag element to canvas
3. Drop within green border (800x480 area)
4. Element appears with snap to grid
5. Move or modify as needed

### Element Manipulation

- **Select**: Click on element (orange border appears)
- **Move**: Drag selected element
- **Delete**: Right-click → Delete
- **Duplicate**: Right-click → Duplicate
- **Properties**: Right-click → Properties (TODO)

### Zoom Controls

- **Slider**: 50% to 200% zoom
- **Percentage**: Displayed next to slider
- **Live Update**: Canvas scales in real-time

### Grid Options

- **Show/Hide**: Toggle grid visibility
- **Snap On/Off**: Toggle snap to grid
- **Grid Size**: Adjustable (5px - 50px)

## Future Enhancements

1. **Properties Dialog**: Implement element property editing
2. **Alignment Tools**: Align left, center, right, top, middle, bottom
3. **Grouping**: Group multiple elements together
4. **Layers**: Z-index management
5. **Copy/Paste**: Clipboard support
6. **Undo/Redo**: History management
7. **Export**: Export canvas as image or code

## API Compatibility

### Iconify API

- **Endpoint**: https://api.iconify.design/search
- **Rate Limit**: No rate limit documented
- **Response Format**: JSON with array of icon names
- **SVG Endpoint**: https://api.iconify.design/{prefix}/{name}.svg
- **Parameters**: color, width, height

### MIME Data Format

```json
{
  "type": "Button|Label|Panel|...",
  "category": "Layout|Testo|Controlli|Input|Speciali"
}
```

## Dependencies

No new dependencies added. Uses existing:
- PyQt6 (GUI framework)
- requests (HTTP client for Iconify API)
- json (MIME data serialization)

## Performance Considerations

- **Icon Cache**: SVG files cached locally to reduce API calls
- **Lazy Loading**: Icons loaded on demand
- **Efficient Rendering**: Qt graphics optimized for large canvas
- **Memory**: Elements use QGraphicsItem for efficient memory usage

## Backward Compatibility

- **Project Files**: Existing projects continue to work
- **API Changes**: Internal only, no external API changes
- **Configuration**: No changes to config format

## Known Limitations

1. **Network Required**: Icon search requires internet (fallback available)
2. **Headless Testing**: GUI tests cannot run in CI without display
3. **Properties Dialog**: Not yet implemented (context menu placeholder)
4. **Element Resize**: Elements cannot be resized yet (planned feature)

## Conclusion

This implementation successfully delivers:
- ✅ Working icon browser with proper Iconify API integration
- ✅ Drag & drop from toolbox to canvas
- ✅ Realistic 5" display visualization with proportions
- ✅ Professional 3D instrument frame
- ✅ 15 element types with unique styles
- ✅ Zoom, grid, and snap features
- ✅ Context menus and element manipulation
- ✅ Comprehensive test suite

All requirements from the problem statement have been met.

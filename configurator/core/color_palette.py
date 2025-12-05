"""
Generatore palette colori e utilità colori
"""

from typing import List, Tuple, Dict
import colorsys


class ColorPaletteGenerator:
    """Generatore palette colori per Metro Digitale"""
    
    # Palette predefinite ottimizzate per display
    PRESETS = {
        "Metro Digitale": ["#1a1a2e", "#16213e", "#00ff88", "#00aaff", "#ff6600"],
        "Dark Pro": ["#0d0d0d", "#1a1a1a", "#00ff00", "#ff0000", "#ffff00"],
        "Ocean": ["#0a192f", "#172a45", "#64ffda", "#8892b0", "#ccd6f6"],
        "Sunset": ["#2d132c", "#801336", "#c72c41", "#ee4540", "#f77f00"],
        "Forest": ["#1b4332", "#2d6a4f", "#40916c", "#52b788", "#74c69d"],
        "Purple Night": ["#240046", "#3c096c", "#5a189a", "#7209b7", "#9d4edd"],
    }
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """
        Converte colore hex in RGB
        
        Args:
            hex_color: Colore in formato #RRGGBB
            
        Returns:
            Tupla (R, G, B) con valori 0-255
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        Converte RGB in hex
        
        Args:
            r, g, b: Valori 0-255
            
        Returns:
            Stringa formato #RRGGBB
        """
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def get_complementary(color: str) -> str:
        """
        Calcola colore complementare
        
        Args:
            color: Colore hex
            
        Returns:
            Colore complementare hex
        """
        r, g, b = ColorPaletteGenerator.hex_to_rgb(color)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # Ruota di 180 gradi
        h = (h + 0.5) % 1.0
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return ColorPaletteGenerator.rgb_to_hex(
            int(r * 255), int(g * 255), int(b * 255)
        )
    
    @staticmethod
    def get_analogous(color: str, count: int = 3) -> List[str]:
        """
        Genera colori analoghi
        
        Args:
            color: Colore base hex
            count: Numero di colori da generare
            
        Returns:
            Lista di colori hex
        """
        r, g, b = ColorPaletteGenerator.hex_to_rgb(color)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        colors = []
        step = 30 / 360  # 30 gradi in frazione
        
        for i in range(count):
            offset = (i - count // 2) * step
            new_h = (h + offset) % 1.0
            
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            hex_color = ColorPaletteGenerator.rgb_to_hex(
                int(r * 255), int(g * 255), int(b * 255)
            )
            colors.append(hex_color)
        
        return colors
    
    @staticmethod
    def get_triadic(color: str) -> List[str]:
        """
        Genera schema triadico (3 colori equidistanti)
        
        Args:
            color: Colore base hex
            
        Returns:
            Lista di 3 colori hex
        """
        r, g, b = ColorPaletteGenerator.hex_to_rgb(color)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        colors = []
        for offset in [0, 1/3, 2/3]:
            new_h = (h + offset) % 1.0
            r, g, b = colorsys.hsv_to_rgb(new_h, s, v)
            hex_color = ColorPaletteGenerator.rgb_to_hex(
                int(r * 255), int(g * 255), int(b * 255)
            )
            colors.append(hex_color)
        
        return colors
    
    @staticmethod
    def generate_palette(base_color: str, count: int = 5, 
                        mode: str = "monochrome") -> List[str]:
        """
        Genera palette da colore base
        
        Args:
            base_color: Colore base hex
            count: Numero di colori da generare
            mode: "monochrome", "analogous", "complementary", "triadic"
            
        Returns:
            Lista di colori hex
        """
        if mode == "monochrome":
            return ColorPaletteGenerator._generate_monochrome(base_color, count)
        elif mode == "analogous":
            return ColorPaletteGenerator.get_analogous(base_color, count)
        elif mode == "complementary":
            comp = ColorPaletteGenerator.get_complementary(base_color)
            return [base_color, comp] + ColorPaletteGenerator._generate_monochrome(base_color, count - 2)
        elif mode == "triadic":
            return ColorPaletteGenerator.get_triadic(base_color)
        else:
            return [base_color] * count
    
    @staticmethod
    def _generate_monochrome(color: str, count: int) -> List[str]:
        """Genera palette monocromatica variando luminosità"""
        r, g, b = ColorPaletteGenerator.hex_to_rgb(color)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        colors = []
        for i in range(count):
            # Varia la luminosità
            factor = 0.3 + (i / (count - 1)) * 0.7 if count > 1 else 1.0
            new_v = v * factor
            
            r, g, b = colorsys.hsv_to_rgb(h, s, new_v)
            hex_color = ColorPaletteGenerator.rgb_to_hex(
                int(r * 255), int(g * 255), int(b * 255)
            )
            colors.append(hex_color)
        
        return colors
    
    @staticmethod
    def lighten(color: str, factor: float = 0.2) -> str:
        """
        Schiarisce un colore
        
        Args:
            color: Colore hex
            factor: Fattore di schiarimento (0-1)
            
        Returns:
            Colore schiarito hex
        """
        r, g, b = ColorPaletteGenerator.hex_to_rgb(color)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        v = min(1.0, v + factor)
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return ColorPaletteGenerator.rgb_to_hex(
            int(r * 255), int(g * 255), int(b * 255)
        )
    
    @staticmethod
    def darken(color: str, factor: float = 0.2) -> str:
        """
        Scurisce un colore
        
        Args:
            color: Colore hex
            factor: Fattore di oscuramento (0-1)
            
        Returns:
            Colore scurito hex
        """
        r, g, b = ColorPaletteGenerator.hex_to_rgb(color)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        v = max(0.0, v - factor)
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return ColorPaletteGenerator.rgb_to_hex(
            int(r * 255), int(g * 255), int(b * 255)
        )

"""
Tooltip Manager - Gestisce tooltip avanzati per elementi UI
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path
from PyQt6.QtWidgets import QToolTip, QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont


class TooltipManager:
    """Gestisce tooltip avanzati con contenuto da file JSON"""
    
    def __init__(self, tooltips_file: Optional[str] = None):
        """
        Inizializza il tooltip manager
        
        Args:
            tooltips_file: Percorso al file JSON con tooltip. Se None, usa il file predefinito.
        """
        self.tooltips_data: Dict = {}
        self._load_tooltips(tooltips_file)
        self._setup_tooltip_style()
    
    def _load_tooltips(self, tooltips_file: Optional[str] = None):
        """Carica tooltip da file JSON"""
        if tooltips_file is None:
            # Cerca file predefinito in resources/guides
            base_dir = Path(__file__).parent.parent
            tooltips_file = base_dir / "resources" / "guides" / "tooltips.json"
        
        try:
            if os.path.exists(tooltips_file):
                with open(tooltips_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tooltips_data = data.get('tooltips', {})
            else:
                print(f"Warning: Tooltips file not found: {tooltips_file}")
                self.tooltips_data = {}
        except Exception as e:
            print(f"Error loading tooltips: {e}")
            self.tooltips_data = {}
    
    def _setup_tooltip_style(self):
        """Configura stile globale tooltip"""
        # Stile CSS per tooltip avanzati
        # Nota: QToolTip styles devono essere applicati a livello di QApplication
        # o singolarmente su ogni widget. Questo metodo prepara lo stile per uso futuro.
        self.tooltip_style = """
            QToolTip {
                background-color: #16213e;
                color: #ffffff;
                border: 2px solid #00ff88;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-family: Arial, sans-serif;
            }
        """
    
    def get_tooltip(self, category: str, key: str) -> Optional[str]:
        """
        Ottiene tooltip da categoria e chiave
        
        Args:
            category: Categoria del tooltip (es. 'elements', 'menus')
            key: Chiave specifica (es. 'Button', 'file')
        
        Returns:
            Testo del tooltip formattato o None se non trovato
        """
        if category not in self.tooltips_data:
            return None
        
        category_data = self.tooltips_data[category]
        if key not in category_data:
            return None
        
        tooltip_info = category_data[key]
        
        # Se è una stringa semplice, ritornala
        if isinstance(tooltip_info, str):
            return tooltip_info
        
        # Se è un dizionario, formatta con HTML
        return self._format_tooltip(tooltip_info)
    
    def _format_tooltip(self, tooltip_info: Dict) -> str:
        """
        Formatta tooltip da dizionario a HTML
        
        Args:
            tooltip_info: Dizionario con informazioni tooltip
        
        Returns:
            HTML formattato per tooltip
        """
        html_parts = []
        
        # Titolo
        if 'title' in tooltip_info:
            html_parts.append(f"<b style='color: #00ff88; font-size: 14px;'>{tooltip_info['title']}</b>")
        
        # Descrizione
        if 'description' in tooltip_info:
            html_parts.append(f"<p style='margin-top: 6px;'>{tooltip_info['description']}</p>")
        
        # Use cases
        if 'use_cases' in tooltip_info and tooltip_info['use_cases']:
            html_parts.append("<p style='margin-top: 6px;'><b>Casi d'uso:</b></p>")
            html_parts.append("<ul style='margin: 0; padding-left: 20px;'>")
            for use_case in tooltip_info['use_cases']:
                html_parts.append(f"<li>{use_case}</li>")
            html_parts.append("</ul>")
        
        # Properties
        if 'properties' in tooltip_info and tooltip_info['properties']:
            html_parts.append("<p style='margin-top: 6px;'><b>Proprietà:</b></p>")
            html_parts.append("<ul style='margin: 0; padding-left: 20px;'>")
            for prop in tooltip_info['properties']:
                html_parts.append(f"<li>{prop}</li>")
            html_parts.append("</ul>")
        
        # Shortcuts
        if 'shortcuts' in tooltip_info and tooltip_info['shortcuts']:
            html_parts.append("<p style='margin-top: 6px;'><b>Scorciatoie:</b></p>")
            html_parts.append("<ul style='margin: 0; padding-left: 20px;'>")
            for shortcut in tooltip_info['shortcuts']:
                html_parts.append(f"<li>{shortcut}</li>")
            html_parts.append("</ul>")
        
        # Features
        if 'features' in tooltip_info and tooltip_info['features']:
            html_parts.append("<p style='margin-top: 6px;'><b>Funzionalità:</b></p>")
            html_parts.append("<ul style='margin: 0; padding-left: 20px;'>")
            for feature in tooltip_info['features']:
                html_parts.append(f"<li>{feature}</li>")
            html_parts.append("</ul>")
        
        return "".join(html_parts)
    
    def set_tooltip(self, widget: QWidget, category: str, key: str):
        """
        Imposta tooltip su widget da categoria e chiave
        
        Args:
            widget: Widget Qt su cui impostare tooltip
            category: Categoria del tooltip
            key: Chiave specifica
        """
        tooltip_text = self.get_tooltip(category, key)
        if tooltip_text:
            widget.setToolTip(tooltip_text)
            widget.setToolTipDuration(5000)  # 5 secondi
    
    def set_element_tooltip(self, widget: QWidget, element_type: str):
        """
        Imposta tooltip per elemento UI
        
        Args:
            widget: Widget elemento
            element_type: Tipo elemento (Button, Label, etc.)
        """
        self.set_tooltip(widget, 'elements', element_type)
    
    def set_menu_tooltip(self, widget: QWidget, menu: str, action: str):
        """
        Imposta tooltip per azione menu
        
        Args:
            widget: Widget azione menu
            menu: Nome menu (file, edit, etc.)
            action: Nome azione (new, save, etc.)
        """
        if 'menus' in self.tooltips_data:
            menus_data = self.tooltips_data['menus']
            if menu in menus_data and action in menus_data[menu]:
                tooltip_text = menus_data[menu][action]
                widget.setToolTip(tooltip_text)
                widget.setToolTipDuration(3000)
    
    def get_shortcuts(self, context: str = 'global') -> Dict[str, str]:
        """
        Ottiene lista scorciatoie per contesto
        
        Args:
            context: Contesto scorciatoie ('global', 'canvas', etc.)
        
        Returns:
            Dizionario con scorciatoie {key: description}
        """
        if 'shortcuts' not in self.tooltips_data:
            return {}
        
        shortcuts_data = self.tooltips_data['shortcuts']
        return shortcuts_data.get(context, {})
    
    def get_guide(self, guide_name: str) -> Optional[Dict]:
        """
        Ottiene guida completa
        
        Args:
            guide_name: Nome guida ('getting_started', 'best_practices', etc.)
        
        Returns:
            Dizionario con informazioni guida
        """
        if 'guides' not in self.tooltips_data:
            return None
        
        guides_data = self.tooltips_data.get('guides', {})
        return guides_data.get(guide_name)
    
    def format_guide_html(self, guide_name: str) -> Optional[str]:
        """
        Formatta guida come HTML
        
        Args:
            guide_name: Nome guida
        
        Returns:
            HTML formattato della guida
        """
        guide = self.get_guide(guide_name)
        if not guide:
            return None
        
        html_parts = []
        
        # Titolo
        if 'title' in guide:
            html_parts.append(f"<h2 style='color: #00ff88;'>{guide['title']}</h2>")
        
        # Steps (se presente)
        if 'steps' in guide:
            html_parts.append("<ol>")
            for step in guide['steps']:
                html_parts.append(f"<li>{step}</li>")
            html_parts.append("</ol>")
        
        # Layout (se presente)
        if 'layout' in guide:
            html_parts.append("<h3>Layout:</h3>")
            html_parts.append("<ul>")
            for tip in guide['layout']:
                html_parts.append(f"<li>{tip}</li>")
            html_parts.append("</ul>")
        
        # Performance (se presente)
        if 'performance' in guide:
            html_parts.append("<h3>Performance:</h3>")
            html_parts.append("<ul>")
            for tip in guide['performance']:
                html_parts.append(f"<li>{tip}</li>")
            html_parts.append("</ul>")
        
        # Usability (se presente)
        if 'usability' in guide:
            html_parts.append("<h3>Usabilità:</h3>")
            html_parts.append("<ul>")
            for tip in guide['usability']:
                html_parts.append(f"<li>{tip}</li>")
            html_parts.append("</ul>")
        
        return "".join(html_parts)
    
    def show_tooltip_at(self, text: str, pos: QPoint, duration: int = 3000):
        """
        Mostra tooltip in posizione specifica
        
        Args:
            text: Testo tooltip
            pos: Posizione globale
            duration: Durata in millisecondi
        """
        QToolTip.showText(pos, text)
    
    @staticmethod
    def create_rich_tooltip(title: str, description: str, 
                           items: Optional[List[str]] = None) -> str:
        """
        Crea tooltip formattato HTML personalizzato
        
        Args:
            title: Titolo tooltip
            description: Descrizione
            items: Lista di voci opzionale
        
        Returns:
            HTML formattato
        """
        html_parts = [
            f"<b style='color: #00ff88; font-size: 14px;'>{title}</b>",
            f"<p style='margin-top: 6px;'>{description}</p>"
        ]
        
        if items:
            html_parts.append("<ul style='margin: 0; padding-left: 20px;'>")
            for item in items:
                html_parts.append(f"<li>{item}</li>")
            html_parts.append("</ul>")
        
        return "".join(html_parts)


# Istanza globale del tooltip manager
_tooltip_manager_instance: Optional[TooltipManager] = None


def get_tooltip_manager() -> TooltipManager:
    """
    Ottiene istanza globale del tooltip manager (singleton)
    
    Returns:
        Istanza TooltipManager
    """
    global _tooltip_manager_instance
    if _tooltip_manager_instance is None:
        _tooltip_manager_instance = TooltipManager()
    return _tooltip_manager_instance


def set_element_tooltip(widget: QWidget, element_type: str):
    """
    Funzione di utilità per impostare tooltip elemento
    
    Args:
        widget: Widget elemento
        element_type: Tipo elemento
    """
    manager = get_tooltip_manager()
    manager.set_element_tooltip(widget, element_type)

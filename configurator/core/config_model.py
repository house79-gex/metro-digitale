"""
Modello dati per la configurazione del Metro Digitale.
Definisce tutte le strutture dati utilizzate nell'applicazione.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class VariabileRilievo:
    """Variabile utilizzata nei calcoli (es: L, H, B)"""
    nome: str
    descrizione: str
    obbligatoria: bool = True
    valore_test: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'descrizione': self.descrizione,
            'obbligatoria': self.obbligatoria,
            'valore_test': self.valore_test
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VariabileRilievo':
        return cls(
            nome=data['nome'],
            descrizione=data['descrizione'],
            obbligatoria=data.get('obbligatoria', True),
            valore_test=data.get('valore_test', 0.0)
        )


@dataclass
class ElementoCalcolato:
    """Elemento calcolato con formula (es: Traversa Anta)"""
    nome: str
    formula: str
    quantita: int = 1
    colore: str = "#00ff88"
    
    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'formula': self.formula,
            'quantita': self.quantita,
            'colore': self.colore
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ElementoCalcolato':
        return cls(
            nome=data['nome'],
            formula=data['formula'],
            quantita=data.get('quantita', 1),
            colore=data.get('colore', '#00ff88')
        )


@dataclass
class TipologiaInfisso:
    """Tipologia di infisso (es: Finestra 2 Ante)"""
    id: str
    nome: str
    icona: str
    categoria: str = "Generica"
    variabili: List[VariabileRilievo] = field(default_factory=list)
    elementi: List[ElementoCalcolato] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'icona': self.icona,
            'categoria': self.categoria,
            'variabili': [v.to_dict() for v in self.variabili],
            'elementi': [e.to_dict() for e in self.elementi]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TipologiaInfisso':
        return cls(
            id=data['id'],
            nome=data['nome'],
            icona=data['icona'],
            categoria=data.get('categoria', 'Generica'),
            variabili=[VariabileRilievo.from_dict(v) for v in data.get('variabili', [])],
            elementi=[ElementoCalcolato.from_dict(e) for e in data.get('elementi', [])]
        )


@dataclass
class MenuItem:
    """Elemento del menu"""
    id: str
    nome: str
    icona: str
    colore: str = "#00ff88"
    ordine: int = 0
    figli: List['MenuItem'] = field(default_factory=list)
    azione: str = "navigate"  # "navigate", "function"
    azione_params: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'icona': self.icona,
            'colore': self.colore,
            'ordine': self.ordine,
            'figli': [f.to_dict() for f in self.figli],
            'azione': self.azione,
            'azione_params': self.azione_params
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MenuItem':
        return cls(
            id=data['id'],
            nome=data['nome'],
            icona=data['icona'],
            colore=data.get('colore', '#00ff88'),
            ordine=data.get('ordine', 0),
            figli=[MenuItem.from_dict(f) for f in data.get('figli', [])],
            azione=data.get('azione', 'navigate'),
            azione_params=data.get('azione_params', {})
        )


@dataclass
class AstinaConfig:
    """Configurazione profilo astina"""
    id: str
    nome: str
    gruppo: str  # "Anta Ribalta", "Persiana", etc.
    offset: float = 0.0
    colore: str = "#00ff88"
    attivo: bool = True
    ordine: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'gruppo': self.gruppo,
            'offset': self.offset,
            'colore': self.colore,
            'attivo': self.attivo,
            'ordine': self.ordine
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AstinaConfig':
        return cls(
            id=data['id'],
            nome=data['nome'],
            gruppo=data['gruppo'],
            offset=data.get('offset', 0.0),
            colore=data.get('colore', '#00ff88'),
            attivo=data.get('attivo', True),
            ordine=data.get('ordine', 0)
        )


@dataclass
class FermavetroConfig:
    """Configurazione fermavetro"""
    id: str
    nome: str
    materiale: str  # "Alluminio", "Legno", "PVC"
    offset: float = 0.0
    colore: str = "#00aaff"
    attivo: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'materiale': self.materiale,
            'offset': self.offset,
            'colore': self.colore,
            'attivo': self.attivo
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FermavetroConfig':
        return cls(
            id=data['id'],
            nome=data['nome'],
            materiale=data['materiale'],
            offset=data.get('offset', 0.0),
            colore=data.get('colore', '#00aaff'),
            attivo=data.get('attivo', True)
        )


@dataclass
class HardwareConfig:
    """Configurazione hardware del dispositivo"""
    encoder: Dict = field(default_factory=lambda: {
        'resolution': 0.01,
        'pulses_per_mm': 100,
        'debounce': 10,
        'pin_a': 4,
        'pin_b': 5,
        'direction': 'normal'
    })
    probes: List[Dict] = field(default_factory=list)
    bluetooth: Dict = field(default_factory=lambda: {
        'name': 'MetroDigitale',
        'uuid': '',
        'auto_connect': False,
        'destinations': []
    })
    display: Dict = field(default_factory=lambda: {
        'width': 800,
        'height': 480,
        'brightness': 100
    })
    
    def to_dict(self) -> Dict:
        return {
            'encoder': self.encoder,
            'probes': self.probes,
            'bluetooth': self.bluetooth,
            'display': self.display
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HardwareConfig':
        return cls(
            encoder=data.get('encoder', {}),
            probes=data.get('probes', []),
            bluetooth=data.get('bluetooth', {}),
            display=data.get('display', {})
        )


@dataclass
class ModeConfig:
    """Configurazione modalità di misura"""
    id: str
    name: str
    category: str = "Generica"
    icon: str = ""
    description: str = ""
    workflow: List[Dict] = field(default_factory=list)
    workflow_notes: str = ""
    formula: str = ""
    unit: str = "mm"
    decimals: int = 2
    bt_enabled: bool = False
    bt_format: str = "JSON"
    bt_prefix: str = ""
    bt_suffix: str = ""
    bt_payload_template: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'icon': self.icon,
            'description': self.description,
            'workflow': self.workflow,
            'workflow_notes': self.workflow_notes,
            'formula': self.formula,
            'unit': self.unit,
            'decimals': self.decimals,
            'bt_enabled': self.bt_enabled,
            'bt_format': self.bt_format,
            'bt_prefix': self.bt_prefix,
            'bt_suffix': self.bt_suffix,
            'bt_payload_template': self.bt_payload_template
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModeConfig':
        return cls(
            id=data['id'],
            name=data['name'],
            category=data.get('category', 'Generica'),
            icon=data.get('icon', ''),
            description=data.get('description', ''),
            workflow=data.get('workflow', []),
            workflow_notes=data.get('workflow_notes', ''),
            formula=data.get('formula', ''),
            unit=data.get('unit', 'mm'),
            decimals=data.get('decimals', 2),
            bt_enabled=data.get('bt_enabled', False),
            bt_format=data.get('bt_format', 'JSON'),
            bt_prefix=data.get('bt_prefix', ''),
            bt_suffix=data.get('bt_suffix', ''),
            bt_payload_template=data.get('bt_payload_template', '')
        )


@dataclass
class UILayout:
    """Configurazione layout UI"""
    theme: str = "dark"
    units: str = "mm"
    decimals: int = 2
    language: str = "it"
    screen_config: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'theme': self.theme,
            'units': self.units,
            'decimals': self.decimals,
            'language': self.language,
            'screen_config': self.screen_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UILayout':
        return cls(
            theme=data.get('theme', 'dark'),
            units=data.get('units', 'mm'),
            decimals=data.get('decimals', 2),
            language=data.get('language', 'it'),
            screen_config=data.get('screen_config', {})
        )


@dataclass
class ProgettoConfigurazione:
    """Progetto completo di configurazione Metro Digitale"""
    schema_version: str = "1.0.0"
    version: str = "1.0.0"
    nome: str = "Nuovo Progetto"
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    
    # Nuovi campi per architettura a 3 schermate
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    modes: List[ModeConfig] = field(default_factory=list)
    ui_layout: UILayout = field(default_factory=UILayout)
    icons: Dict = field(default_factory=dict)
    
    # Campi esistenti
    menus: List[MenuItem] = field(default_factory=list)
    tipologie: List[TipologiaInfisso] = field(default_factory=list)
    astine: List[AstinaConfig] = field(default_factory=list)
    fermavetri: List[FermavetroConfig] = field(default_factory=list)
    impostazioni: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'schema_version': self.schema_version,
            'version': self.version,
            'nome': self.nome,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'hardware': self.hardware.to_dict(),
            'modes': [m.to_dict() for m in self.modes],
            'ui_layout': self.ui_layout.to_dict(),
            'icons': self.icons,
            'menus': [m.to_dict() for m in self.menus],
            'tipologie': [t.to_dict() for t in self.tipologie],
            'astine': [a.to_dict() for a in self.astine],
            'fermavetri': [f.to_dict() for f in self.fermavetri],
            'impostazioni': self.impostazioni
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProgettoConfigurazione':
        return cls(
            schema_version=data.get('schema_version', '1.0.0'),
            version=data.get('version', '1.0.0'),
            nome=data.get('nome', 'Progetto'),
            created=datetime.fromisoformat(data.get('created', datetime.now().isoformat())),
            modified=datetime.fromisoformat(data.get('modified', datetime.now().isoformat())),
            hardware=HardwareConfig.from_dict(data.get('hardware', {})) if 'hardware' in data else HardwareConfig(),
            modes=[ModeConfig.from_dict(m) for m in data.get('modes', [])],
            ui_layout=UILayout.from_dict(data.get('ui_layout', {})) if 'ui_layout' in data else UILayout(),
            icons=data.get('icons', {}),
            menus=[MenuItem.from_dict(m) for m in data.get('menus', [])],
            tipologie=[TipologiaInfisso.from_dict(t) for t in data.get('tipologie', [])],
            astine=[AstinaConfig.from_dict(a) for a in data.get('astine', [])],
            fermavetri=[FermavetroConfig.from_dict(f) for f in data.get('fermavetri', [])],
            impostazioni=data.get('impostazioni', {})
        )

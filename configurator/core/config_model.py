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
class ModeWorkflowStep:
    """Passo nel workflow di una modalità di misura"""
    id: str
    description: str
    variable: str  # Variabile da acquisire (es: "L", "H")
    probe_type: str = "internal"  # "internal", "external", "depth", "step"
    constraints: Dict = field(default_factory=dict)  # Vincoli opzionali
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'description': self.description,
            'variable': self.variable,
            'probe_type': self.probe_type,
            'constraints': self.constraints
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModeWorkflowStep':
        return cls(
            id=data['id'],
            description=data['description'],
            variable=data['variable'],
            probe_type=data.get('probe_type', 'internal'),
            constraints=data.get('constraints', {})
        )


@dataclass
class MeasureMode:
    """Modalità di misura con workflow e formule"""
    id: str
    nome: str
    categoria: str
    icona: str
    workflow: List[ModeWorkflowStep] = field(default_factory=list)
    formule: Dict[str, str] = field(default_factory=dict)  # {nome_risultato: formula}
    send_bt: bool = True  # Invia automaticamente via Bluetooth
    bt_payload_template: str = ""  # Template per payload BT
    unita: str = "mm"
    decimali: int = 2
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'categoria': self.categoria,
            'icona': self.icona,
            'workflow': [s.to_dict() for s in self.workflow],
            'formule': self.formule,
            'send_bt': self.send_bt,
            'bt_payload_template': self.bt_payload_template,
            'unita': self.unita,
            'decimali': self.decimali
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MeasureMode':
        return cls(
            id=data['id'],
            nome=data['nome'],
            categoria=data['categoria'],
            icona=data['icona'],
            workflow=[ModeWorkflowStep.from_dict(s) for s in data.get('workflow', [])],
            formule=data.get('formule', {}),
            send_bt=data.get('send_bt', True),
            bt_payload_template=data.get('bt_payload_template', ''),
            unita=data.get('unita', 'mm'),
            decimali=data.get('decimali', 2)
        )


@dataclass
class ProgettoConfigurazione:
    """Progetto completo di configurazione Metro Digitale"""
    version: str = "1.0.0"
    schema_version: str = "2.0.0"  # Nuova versione schema
    nome: str = "Nuovo Progetto"
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    menus: List[MenuItem] = field(default_factory=list)
    tipologie: List[TipologiaInfisso] = field(default_factory=list)
    astine: List[AstinaConfig] = field(default_factory=list)
    fermavetri: List[FermavetroConfig] = field(default_factory=list)
    modes: List[MeasureMode] = field(default_factory=list)  # Nuove modalità di misura
    hardware: Dict = field(default_factory=dict)  # Configurazione hardware
    ui_layout: Dict = field(default_factory=dict)  # Layout UI
    icons: Dict = field(default_factory=dict)  # Registry icone locali
    impostazioni: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'version': self.version,
            'schema_version': self.schema_version,
            'nome': self.nome,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'menus': [m.to_dict() for m in self.menus],
            'tipologie': [t.to_dict() for t in self.tipologie],
            'astine': [a.to_dict() for a in self.astine],
            'fermavetri': [f.to_dict() for f in self.fermavetri],
            'modes': [m.to_dict() for m in self.modes],
            'hardware': self.hardware,
            'ui_layout': self.ui_layout,
            'icons': self.icons,
            'impostazioni': self.impostazioni
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProgettoConfigurazione':
        return cls(
            version=data.get('version', '1.0.0'),
            schema_version=data.get('schema_version', '2.0.0'),
            nome=data.get('nome', 'Progetto'),
            created=datetime.fromisoformat(data.get('created', datetime.now().isoformat())),
            modified=datetime.fromisoformat(data.get('modified', datetime.now().isoformat())),
            menus=[MenuItem.from_dict(m) for m in data.get('menus', [])],
            tipologie=[TipologiaInfisso.from_dict(t) for t in data.get('tipologie', [])],
            astine=[AstinaConfig.from_dict(a) for a in data.get('astine', [])],
            fermavetri=[FermavetroConfig.from_dict(f) for f in data.get('fermavetri', [])],
            modes=[MeasureMode.from_dict(m) for m in data.get('modes', [])],
            hardware=data.get('hardware', {}),
            ui_layout=data.get('ui_layout', {}),
            icons=data.get('icons', {}),
            impostazioni=data.get('impostazioni', {})
        )

"""
Configurazione hardware Metro Digitale
Definisce strutture dati per encoder, puntali, modalità operative e Bluetooth
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class TipoPuntale(Enum):
    """Tipi di puntale disponibili"""
    STANDARD = "standard"
    INTERNO = "interno"
    ESTERNO = "esterno"
    PROFONDITA = "profondità"
    BATTUTA = "battuta"


class ModalitaMisura(Enum):
    """Modalità di misurazione disponibili"""
    CALIBRO = "calibro"
    VETRI = "vetri"
    ASTINE = "astine"
    FERMAVETRI = "fermavetri"
    TIPOLOGIE = "tipologie"


@dataclass
class EncoderConfig:
    """Configurazione encoder rotativo"""
    risoluzione: int = 400  # Impulsi per rotazione
    pin_clk: int = 2  # Pin CLK (GPIO)
    pin_dt: int = 3  # Pin DT (GPIO)
    pin_sw: int = 4  # Pin pulsante (GPIO)
    fattore_calibrazione: float = 1.0  # Fattore di correzione
    inversione: bool = False  # Inverti direzione
    debounce_ms: int = 5  # Tempo debounce in millisecondi
    
    def to_dict(self) -> Dict:
        """Converte in dizionario"""
        return {
            "risoluzione": self.risoluzione,
            "pin_clk": self.pin_clk,
            "pin_dt": self.pin_dt,
            "pin_sw": self.pin_sw,
            "fattore_calibrazione": self.fattore_calibrazione,
            "inversione": self.inversione,
            "debounce_ms": self.debounce_ms
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea da dizionario"""
        return cls(**data)


@dataclass
class PuntaleConfig:
    """Configurazione puntale di misura"""
    tipo: TipoPuntale = TipoPuntale.STANDARD
    nome: str = "Puntale Standard"
    offset_mm: float = 0.0  # Offset da aggiungere alla misura
    diametro_mm: float = 10.0  # Diametro puntale
    lunghezza_mm: float = 50.0  # Lunghezza puntale
    descrizione: str = ""
    
    def to_dict(self) -> Dict:
        """Converte in dizionario"""
        return {
            "tipo": self.tipo.value,
            "nome": self.nome,
            "offset_mm": self.offset_mm,
            "diametro_mm": self.diametro_mm,
            "lunghezza_mm": self.lunghezza_mm,
            "descrizione": self.descrizione
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea da dizionario"""
        data_copy = data.copy()
        if "tipo" in data_copy:
            data_copy["tipo"] = TipoPuntale(data_copy["tipo"])
        return cls(**data_copy)
    
    @staticmethod
    def get_presets() -> List['PuntaleConfig']:
        """Restituisce puntali preimpostati"""
        return [
            PuntaleConfig(
                tipo=TipoPuntale.STANDARD,
                nome="Puntale Standard",
                offset_mm=0.0,
                diametro_mm=10.0,
                descrizione="Puntale standard per misure generiche"
            ),
            PuntaleConfig(
                tipo=TipoPuntale.INTERNO,
                nome="Puntale Interno",
                offset_mm=-5.0,
                diametro_mm=8.0,
                descrizione="Puntale per misure interne (cave, fori)"
            ),
            PuntaleConfig(
                tipo=TipoPuntale.ESTERNO,
                nome="Puntale Esterno",
                offset_mm=5.0,
                diametro_mm=12.0,
                descrizione="Puntale per misure esterne"
            ),
            PuntaleConfig(
                tipo=TipoPuntale.PROFONDITA,
                nome="Puntale Profondità",
                offset_mm=0.0,
                diametro_mm=6.0,
                lunghezza_mm=100.0,
                descrizione="Puntale per misure di profondità"
            ),
            PuntaleConfig(
                tipo=TipoPuntale.BATTUTA,
                nome="Puntale Battuta",
                offset_mm=10.0,
                diametro_mm=15.0,
                descrizione="Puntale per misure con battuta"
            ),
        ]


@dataclass
class ModalitaOperativa:
    """Configurazione modalità operativa"""
    modalita: ModalitaMisura = ModalitaMisura.CALIBRO
    nome: str = "Calibro Semplice"
    descrizione: str = ""
    puntale: Optional[PuntaleConfig] = None
    parametri: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Converte in dizionario"""
        return {
            "modalita": self.modalita.value,
            "nome": self.nome,
            "descrizione": self.descrizione,
            "puntale": self.puntale.to_dict() if self.puntale else None,
            "parametri": self.parametri
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea da dizionario"""
        data_copy = data.copy()
        if "modalita" in data_copy:
            data_copy["modalita"] = ModalitaMisura(data_copy["modalita"])
        if "puntale" in data_copy and data_copy["puntale"]:
            data_copy["puntale"] = PuntaleConfig.from_dict(data_copy["puntale"])
        return cls(**data_copy)
    
    @staticmethod
    def get_presets() -> List['ModalitaOperativa']:
        """Restituisce modalità preimpostate"""
        return [
            ModalitaOperativa(
                modalita=ModalitaMisura.CALIBRO,
                nome="Calibro Semplice",
                descrizione="Misura diretta con calibro digitale",
                parametri={"unita": "mm", "precisione": 0.01}
            ),
            ModalitaOperativa(
                modalita=ModalitaMisura.VETRI,
                nome="Vetri LxA",
                descrizione="Misura vetri con larghezza x altezza",
                parametri={"tolleranza": 2.0, "formato": "LxA"}
            ),
            ModalitaOperativa(
                modalita=ModalitaMisura.ASTINE,
                nome="Astine Anta-Ribalta",
                descrizione="Misura astine per anta ribalta",
                parametri={"tipo": "anta_ribalta", "battuta": True}
            ),
            ModalitaOperativa(
                modalita=ModalitaMisura.FERMAVETRI,
                nome="Fermavetri Standard",
                descrizione="Misura fermavetri standard",
                parametri={"tipo": "standard"}
            ),
            ModalitaOperativa(
                modalita=ModalitaMisura.TIPOLOGIE,
                nome="Tipologia Finestra",
                descrizione="Misura per tipologie finestre predefinite",
                parametri={"template": "finestra_1a"}
            ),
        ]


@dataclass
class BluetoothConfig:
    """Configurazione Bluetooth"""
    abilitato: bool = True
    nome_dispositivo: str = "MetroDigitale"
    uuid_servizio: str = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
    uuid_caratteristica: str = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
    protocollo: str = "BLE"  # BLE o Classic
    pin_pairing: str = "1234"
    auto_reconnect: bool = True
    timeout_s: int = 30
    
    def to_dict(self) -> Dict:
        """Converte in dizionario"""
        return {
            "abilitato": self.abilitato,
            "nome_dispositivo": self.nome_dispositivo,
            "uuid_servizio": self.uuid_servizio,
            "uuid_caratteristica": self.uuid_caratteristica,
            "protocollo": self.protocollo,
            "pin_pairing": self.pin_pairing,
            "auto_reconnect": self.auto_reconnect,
            "timeout_s": self.timeout_s
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea da dizionario"""
        return cls(**data)


@dataclass
class HardwareConfig:
    """Configurazione hardware completa Metro Digitale"""
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    puntali: List[PuntaleConfig] = field(default_factory=list)
    puntale_corrente: Optional[PuntaleConfig] = None
    modalita: List[ModalitaOperativa] = field(default_factory=list)
    modalita_corrente: Optional[ModalitaOperativa] = None
    bluetooth: BluetoothConfig = field(default_factory=BluetoothConfig)
    
    def __post_init__(self):
        """Inizializza con valori predefiniti se vuoti"""
        if not self.puntali:
            self.puntali = PuntaleConfig.get_presets()
        if not self.puntale_corrente and self.puntali:
            self.puntale_corrente = self.puntali[0]
        if not self.modalita:
            self.modalita = ModalitaOperativa.get_presets()
        if not self.modalita_corrente and self.modalita:
            self.modalita_corrente = self.modalita[0]
    
    def to_dict(self) -> Dict:
        """Converte in dizionario"""
        return {
            "encoder": self.encoder.to_dict(),
            "puntali": [p.to_dict() for p in self.puntali],
            "puntale_corrente": self.puntale_corrente.to_dict() if self.puntale_corrente else None,
            "modalita": [m.to_dict() for m in self.modalita],
            "modalita_corrente": self.modalita_corrente.to_dict() if self.modalita_corrente else None,
            "bluetooth": self.bluetooth.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea da dizionario"""
        data_copy = data.copy()
        if "encoder" in data_copy:
            data_copy["encoder"] = EncoderConfig.from_dict(data_copy["encoder"])
        if "puntali" in data_copy:
            data_copy["puntali"] = [PuntaleConfig.from_dict(p) for p in data_copy["puntali"]]
        if "puntale_corrente" in data_copy and data_copy["puntale_corrente"]:
            data_copy["puntale_corrente"] = PuntaleConfig.from_dict(data_copy["puntale_corrente"])
        if "modalita" in data_copy:
            data_copy["modalita"] = [ModalitaOperativa.from_dict(m) for m in data_copy["modalita"]]
        if "modalita_corrente" in data_copy and data_copy["modalita_corrente"]:
            data_copy["modalita_corrente"] = ModalitaOperativa.from_dict(data_copy["modalita_corrente"])
        if "bluetooth" in data_copy:
            data_copy["bluetooth"] = BluetoothConfig.from_dict(data_copy["bluetooth"])
        return cls(**data_copy)
    
    @staticmethod
    def get_default() -> 'HardwareConfig':
        """Restituisce configurazione hardware predefinita"""
        return HardwareConfig()

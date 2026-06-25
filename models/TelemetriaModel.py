from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TelemetriaModel:
    # Identificadores do Dispositivo e Frota
    codigo_empresa: str
    placa: str
    mac_scanner: str
    mac_rasp: str
    
    # Dados de Telemetria
    rpm: int
    velocidade: float
    odometro: float
    
    # Metadados
    timestamp: str = None
    status: str = "ativo"

    def __post_init__(self):
        # Define o timestamp automaticamente se não for fornecido
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        """Retorna o objeto como um dicionário para o JSON da API"""
        return asdict(self)
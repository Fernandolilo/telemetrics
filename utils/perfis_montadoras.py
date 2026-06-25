import re

# Correção: Agora as fórmulas tratam o Hexa como um bloco único completo
PERFIS_MONTADORAS = {
    
    "obd2_generico": {
        "init_cmds": ["ATZ", "ATSP0"],
        "pid": "010C", # RPM como teste
        "regex": r"410C([0-9A-Fa-f]{4})",
        "formula": lambda h: int(h, 16) / 4.0
    },
    "renault_ecu_engine": {
        "init_cmds": ["ATSH7E0", "ATCRA7E8"],
        "pid": "222002",
        "regex": r"622002([0-9A-Fa-f]+)",
        # Fórmula corrigida para processar o hex completo sem truncar
        "formula": lambda hex_val: int(hex_val, 16)
    },
    "renault_kwid_2019": {
        "init_cmds": ["ATSH7E0", "ATCRA7E8"], # Cabeçalhos padrão Renault
        "pid": "222006",
        "regex": r"622006([0-9A-Fa-f]{6})", # Odo com 3 bytes (6 hex)
        "formula": lambda h: int(h, 16) / 1.0 # Ajuste a divisão se precisar (ex: /10)
    }
    # ... (mantenha os outros perfis seguindo este padrão)
}

class LeitorOdometroOBD:
    def __init__(self, perfis):
        self.perfis = perfis

    def limpar_resposta(self, raw_response: str) -> str:
        # Corrigido o nome do método para limpar_resposta
        return re.sub(r'(SEARCHING\.\.\.|[\s>\r\n])', '', raw_response).upper()

    def processar_resposta(self, montadora: str, raw_response: str) -> float:
        if montadora not in self.perfis:
            raise ValueError(f"Perfil '{montadora}' não cadastrado.")
            
        perfil = self.perfis[montadora]
        string_limpa = self.limpar_resposta(raw_response)
        
        match = re.search(perfil["regex"], string_limpa)
        if not match:
            raise ValueError(f"Regex não encontrou dado em: {string_limpa}")
            
        hex_capturado = match.group(1)
        # O segredo para ler 100.000km está aqui: 
        # int(hex_capturado, 16) converte a string hex completa para decimal
        resultado = perfil["formula"](hex_capturado)
        return float(resultado)
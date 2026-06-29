import re
import asyncio
from utils.perfis_montadoras import PERFIS_MONTADORAS

class OBDTelemetry:

    def __init__(self, bt):
        self.bt = bt
        self.rpm_history = []

    # Em services/OBDTelemetry.py
    async def start_session(self):
        print("[OBD] Resetando adaptador...")
        # Adicione este check de segurança
        if not self.bt.client or not self.bt.client.is_connected:
            await self.bt.ensure_connected() 
        
        await self.bt.send("ATZ", delay=0.5)
    # ...

    async def get_rpm(self):
        resp = await self.bt.send("010C", delay=0.2)
        rpm = self._parse_rpm(resp)
        return self._smooth_rpm(rpm)

    async def get_speed(self):
        resp = await self.bt.send("010D", delay=0.2)
        return self._parse_speed(resp)

    # =========================================================================
    # ENTRADA DO NOVO MOTOR: SCAN COMPLETO EM VEZ DE PARAR NO PRIMEIRO SUCESSO
    # =========================================================================
    async def scan_all_modules(self):
        """
        Varredura Avançada de Módulos.
        Testa 100% dos perfis cadastrados e retorna um dicionário 
        com tudo o que foi possível extrair do veículo.
        """
        print("\n🔍 [VARREDURA TOTAL] Iniciando mapeamento completo de módulos...")
        relatorio_veiculo = {}

        for idx, (nome_perfil, conf) in enumerate(PERFIS_MONTADORAS.items(), 1):
            print(f"⚡ [{idx}/{len(PERFIS_MONTADORAS)}] Escaneando barramento via: {nome_perfil}")
            
            # Limpa o buffer e os barramentos anteriores no chip
            await self.bt.send("ATAR", delay=0.05)
            
            # Aplica os comandos de cabeçalho (ATSH / ATCRA)
            for cmd in conf["init_cmds"]:
                await self.bt.send(cmd, delay=0.1)
            
            # Envia o PID estendido do módulo atual
            resp = await self.bt.send(conf["pid"], delay=0.6)
            
            if not resp:
                continue
                
            resp_upper = resp.upper().strip()
            resp_clean = re.sub(r'(SEARCHING\.\.\.|[\s>\r\n])', '', resp_upper)
            
            # Se o módulo rejeitar o comando, pula para o próximo sem salvar erro
            if any(msg in resp_clean for msg in ["NODATA", "ERROR", "UNABLE", "?", "STOPPED"]):
                continue

            # Processa o dado capturado usando o validador matemático
            dado_calculado = self._parse_odometer(resp_clean, conf)
            
            if dado_calculado is not None:
                print(f"   --> ✨ Dados encontrados em {nome_perfil}: {dado_calculado} km")
                # Armazena o achado no relatório
                relatorio_veiculo[nome_perfil] = {
                    "modulo": nome_perfil.split("_")[1].upper(), # Extrai 'PAINEL', 'ECU' ou 'ABS'
                    "valor": dado_calculado,
                    "unidade": "km",
                    "pid_origem": conf["pid"],
                    "hex_bruto": resp_clean
                }

        print("\n📊 [FIM DA VARREDURA] Mapeamento concluído.")
        
        # Restaura os canais padrão do chip para não travar a telemetria depois
        await self.bt.send("ATZ", delay=0.5)
        await self.bt.send("ATE0", delay=0.2)
        await self.bt.send("ATSP0", delay=0.2)
        
        return relatorio_veiculo

    # =========================================================================
    # PARSERS INTERNOS DA CLASSE
    # =========================================================================
    def _parse_rpm(self, resp):
        if not resp or "NODATA" in resp.upper(): return 0
        m = re.search(r"410C([0-9A-Fa-f]{4})", resp)
        if not m: return 0
        value = int(m.group(1), 16)
        return 0 if (value / 4) < 150 else (value / 4)

    def _parse_speed(self, resp):
        if not resp or "NODATA" in resp.upper(): return 0
        m = re.search(r"410D([0-9A-Fa-f]{2})", resp)
        if not m: return 0
        return int(m.group(1), 16)

    def _parse_odometer(self, resp_clean, conf):
        m = re.search(conf["regex"], resp_clean)
        if not m: return None
        
        hex_dados = m.group(1)
        print(f"DEBUG: Hex bruto capturado = {hex_dados}") # Adicione esta linha
        
        try:
            # Tente converter todo o hex para ver o valor decimal real
            valor_inteiro = int(hex_dados, 16)
            print(f"DEBUG: Valor decimal convertido = {valor_inteiro}")
            
            km_calculado = conf["formula"](hex_dados)
            return round(km_calculado, 1)
        except Exception as e:
            print(f"   Erro: {e}")
        return None
    
    async def dump_modulo_completo(self, perfil_nome):
        conf = PERFIS_MONTADORAS[perfil_nome]
        
        # 1. Configurar o endereço de transmissão (ATSH) e recebimento (ATCRA)
        # Isso é o que faz o carro "ouvir" a sua pergunta
        for cmd in conf["init_cmds"]:
            await self.bt.send(cmd, delay=0.1)
            
        # 2. Enviar o PID
        resp = await self.bt.send(conf["pid"], delay=1.0)
        
        # A string limpa vai nos dizer se agora o carro respondeu
        print(f"Resposta BRUTA: {resp}")
        
    async def varredura_serie(self, range_start=0x2000, range_end=0x20FF):
        print(f"\n🚀 Varredura ATIVA iniciada. Olhando para o terminal...")
        
        for pid_int in range(range_start, range_end + 1):
            pid_hex = hex(pid_int)[2:].upper()
            comando = f"22{pid_hex}"
            
            # Envia o comando
            resp = await self.bt.send(comando, delay=0.1)
            
            # PROTEÇÃO: Se resp for None, pula para o próximo PID
            if resp is None:
                continue
                
            # Limpa e verifica se há resposta
            resp_limpa = re.sub(r'[\s>\r\n]', '', resp.upper())
            
            # Se a resposta contiver '62', é um sucesso!
            if "62" in resp_limpa:
                print(f"!!! ENCONTRADO: {comando} -> RESPOSTA: {resp_limpa} !!!")
            elif pid_int % 10 == 0:
                # Mostra progresso sem poluir muito o terminal
                print(f"Testando... {comando}", end="\r")

    def _smooth_rpm(self, rpm):
        self.rpm_history.append(rpm)
        if len(self.rpm_history) > 5: 
            self.rpm_history.pop(0)
        return sum(self.rpm_history) / len(self.rpm_history)
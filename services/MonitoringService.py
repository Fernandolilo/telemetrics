import asyncio
import logging

# Se o seu leitor ou telemetria exigirem algum tipo de conversão, 
# adicione aqui, mas o essencial para o funcionamento do loop é:
class MonitoringService:
    def __init__(self, bt, telemetria, leitor):
        self.bt = bt
        self.telemetria = telemetria
        self.leitor = leitor
        
        # Variáveis de estado para persistir os dados entre leituras
        self.rpm = 0
        self.speed = 0
        self.odometro = 0

    async def run_monitor(self, modelo, conf):
        print(f"\n🔧 Aplicando protocolo para: {modelo}")
        for cmd in conf["init_cmds"]:
            await self.bt.send(cmd, delay=0.1)
        
        print(f"\n=== MONITORAMENTO {modelo.upper()} ===")
        
        while True:
            try:
                # Captura dos dados do sensor
                self.rpm = await self.telemetria.get_rpm()
                self.speed = await self.telemetria.get_speed()
                resp = await self.bt.send(conf["pid"], delay=0.2)
                
                try:
                    self.odometro = self.leitor.processar_resposta(modelo, resp)
                except Exception as e:
                    # Log de erro silencioso para o odômetro não parar o monitoramento
                    self.odometro = 0

                # Exibição no console
                print(f"RPM: {int(self.rpm):4} | Speed: {self.speed:3} km/h | Odometro: {self.odometro} km")
                
                await asyncio.sleep(1)
            except Exception as e:
                print(f"\nErro no loop de monitoramento: {e}")
                await asyncio.sleep(2)

    def get_data(self):
        """Método para o VehicleController consultar o estado atual"""
        return {
            "rpm": self.rpm,
            "velocidade": self.speed,
            "odometro": self.odometro
        }
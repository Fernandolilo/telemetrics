import asyncio
import re
import json
from datetime import datetime

class DomainController:
    def __init__(self, bt_adapter):
        self.bt = bt_adapter
        self.state = {
            "vehicle": {
                "identification": {"placa": "RUG8E03", "device_id": "1"},
                "telemetry": {"current": {"rpm": 0, "velocidade": 0}, "history": []}
            },
            "last_update": None
        }
        self.is_running = False

    async def run_telemetry_loop(self):
        """Loop de monitoramento: roda a cada 30s sem bloquear a API"""
        print("[DOMÍNIO] Iniciando loop de telemetria...")
        await self._init_obd_session()
        
        while True:
            try:
                # Coleta dados vitais
                rpm = await self._get_rpm_safe()
                speed = await self._get_speed_safe()
                
                # Atualiza o estado
                self.state["vehicle"]["telemetry"]["current"] = {
                    "rpm": rpm,
                    "velocidade": speed,
                    "odometro": 0 # Pode ser lido menos frequentemente
                }
                self.state["last_update"] = datetime.now().isoformat()
                
                # Salva em arquivo para persistência (facilita o acesso da API)
                with open("device_state.json", "w") as f:
                    json.dump(self.state, f)
                    
            except Exception as e:
                print(f"[DOMÍNIO] Erro no loop: {e}")
            
            await asyncio.sleep(30)

    async def _init_obd_session(self):
        await self.bt.send("ATZ")
        await asyncio.sleep(0.5)
        await self.bt.send("ATE0")
        await self.bt.send("ATSP0")

    async def _get_rpm_safe(self):
        resp = await self.bt.send("010C")
        # Logica do seu parser aqui...
        return 0 # Placeholder

    async def _get_speed_safe(self):
        resp = await self.bt.send("010D")
        return 0 # Placeholder

# --- Integração com o Flask ---
# No seu arquivo principal de inicialização:
# loop = asyncio.new_event_loop()
# controller = DomainController(bt_adapter)
# threading.Thread(target=loop.run_forever, daemon=True).start()
# asyncio.run_coroutine_threadsafe(controller.run_telemetry_loop(), loop)
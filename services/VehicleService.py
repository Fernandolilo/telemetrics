import json
import os

class VehicleService:

    def __init__(self, storage_dir="data"):
        self.storage_dir = storage_dir
        self.config_file = os.path.join(storage_dir, "config.json")

    # ==========================
    # CONFIG
    # ==========================
    def get_config(self):

        if not os.path.exists(self.config_file):
            return None

        with open(self.config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # ==========================
    # CURRENT TELEMETRY
    # ==========================
    def get_current(self, placa):

        file_path = os.path.join(self.storage_dir, f"{placa}_current.json")

        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ==========================
    # HISTORY
    # ==========================
    def get_history(self, placa):

        history = []

        for file_name in os.listdir(self.storage_dir):

            if (
                file_name.startswith(placa)
                and file_name.endswith(".json")
                and "current" not in file_name
                and file_name != "config.json"
            ):
                file_path = os.path.join(self.storage_dir, file_name)

                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        history.extend(json.load(f))
                    except json.JSONDecodeError:
                        pass

        return history

    # ==========================
    # VALIDATION
    # ==========================
    def validate_vehicle(self, placa, config):
    
        print("PLACA PESQUISADA:", placa)
        print("PLACA CONFIG:", config.get("placa"))

        if not config:
            return False

        return config.get("placa", "").strip().upper() == placa.strip().upper()

    # ==========================
    # MAIN FIND
    # ==========================
    def find_by_placa(self, placa):
        placa = placa.strip().upper()
        config = self.get_config()

        if not self.validate_vehicle(placa, config):
            return {"ok": False, "error": "Placa não cadastrada"}

        current = self.get_current(placa)
        history = self.get_history(placa)

        # RETORNO PADRONIZADO
        return {
            "ok": True,
            "data": {
                "vehicle": {
                    "identification": {
                        "placa": placa,
                        "device_id": config.get("device_id", "N/A"),
                        "codigo_empresa": config.get("codigo_empresa", "N/A")
                    },
                    "telemetry": {
                        "current": current or {},
                        "history": history or []
                    }
                }
            }
        }
import json
import os
from datetime import datetime

class TelemetryService:

    def __init__(self, storage_dir="data"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

        self.telemetry_file = os.path.join(self.storage_dir, "telemetria.json")
        self.config_file = os.path.join(self.storage_dir, "config.json")

    # =========================
    # TELEMETRIA (HISTÓRICO)
    # =========================
    def save_telemetria(self, model_instance):

        data = model_instance.to_dict()

        filename = f"{model_instance.placa}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.storage_dir, filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        else:
            history = []

        history.append(data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"✔ Telemetria salva em {filepath}")

    # =========================
    # CONFIG (ÚNICO REGISTRO)
    # =========================
    def save_config(self, data: dict):

        payload = {
            **data,
            "timestamp": datetime.now().isoformat()
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

        print(f"✔ Config salva em {self.config_file}")
        return payload
import json
import os
from datetime import datetime

class TelemetryStateService:

    def __init__(self, storage_dir="data"):

        self.filepath = os.path.join(storage_dir, "telemetria_current.json")
        self.history_path = os.path.join(storage_dir, "telemetria_history.json")

        os.makedirs(storage_dir, exist_ok=True)

    def update(self, data: dict):

        payload = {
            **data,
            "timestamp": datetime.now().isoformat()
        }

        # 1. atualiza estado atual
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

        # 2. adiciona histórico
        history = []

        if os.path.exists(self.history_path):
            with open(self.history_path, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except:
                    history = []

        history.append(payload)

        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        return payload

    def get_current(self):

        if not os.path.exists(self.filepath):
            return None

        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)
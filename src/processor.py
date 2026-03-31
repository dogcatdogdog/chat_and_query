import json
import os
from typing import Dict, Any

class DataProcessor:
    def __init__(self, db_path: str = "data/mock_db.json"):
        self.db_path = db_path
        self.VALID_DEVICES = ["UAV-SN-001", "UAV-SN-002", "UAV-SN-005", "UAV-SN-008"]

    def _get_db(self):
        if not os.path.exists(self.db_path):
            return {}
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def call_api(self, path: str, params: dict = {}) -> Dict[str, Any]:
        db = self._get_db()
        p = path.strip().upper()
        
        if "MISSIONS/STATS" in p:
            return db.get("missions", {}).get("summary", {})
        
        if "DEVICES/COUNT" in p:
            devices = db.get("devices", {})
            return {"online": devices.get("online_count"), "offline": devices.get("offline_count"), "total": devices.get("total")}
        
        if "TELEMETRY" in p:
            sn = params.get("sn")
            if not sn or sn not in self.VALID_DEVICES:
                return {"error": f"Device Not Found: {sn}", "code": 404}
            return {
                "sn": sn, "status": "FLYING", "battery": 85,
                "location": {"lat": 30.281, "lng": 120.162, "alt": 150.0},
                "telemetry": {"speed": 8.5, "pitch": -5.0}
            }
            
        if "EVENTS/ANALYSIS" in p:
            return db.get("events", {})

        return {"error": "API Path Mismatch", "path": path}

processor = DataProcessor()

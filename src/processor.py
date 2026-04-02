import json
import os
from typing import Dict, Any

class DataProcessor:
    def __init__(self, db_path: str = "data/mock_db.json"):
        self.db_path = db_path
        # 统一使用 UAV-00x 格式
        self.VALID_DEVICES = ["UAV-001", "UAV-002", "UAV-005", "UAV-008"]

    def _get_db(self):
        if not os.path.exists(self.db_path):
            return {}
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def call_api(self, path: str, params: dict = {}) -> Dict[str, Any]:
        db = self._get_db()
        p = path.strip().upper()
        
        # 1. 任务相关
        if "MISSIONS/STATS" in p:
            return db.get("missions", {}).get("summary", {})
        if "MISSIONS/LIST" in p:
            return {"active_missions": db.get("missions", {}).get("active_list", [])}
        
        # 2. 设备相关
        if "DEVICES/COUNT" in p or "DEVICES/LIST" in p:
            devices = db.get("devices", {})
            status_filter = params.get("status", "").lower()
            response = {
                "online_count": devices.get("online_count"),
                "offline_count": devices.get("offline_count"),
                "total": devices.get("total")
            }
            if status_filter == "online":
                response["list"] = devices.get("online_list", [])
            elif status_filter == "offline":
                response["list"] = devices.get("offline_list", [])
            else:
                response["online_list"] = devices.get("online_list", [])
                response["offline_list"] = devices.get("offline_list", [])
            return response
            
        if "TELEMETRY" in p:
            sn = params.get("sn")
            if not sn or sn not in self.VALID_DEVICES:
                return {"error": f"Device Not Found: {sn}", "code": 404}
            # 模拟实时数据
            return {
                "sn": sn, "status": "FLYING" if "001" in sn else "STANDBY", "battery": 82,
                "location": {"lat": 30.28, "lng": 120.16, "alt": 150.0},
                "telemetry": {"speed": 5.2, "pitch": -2.0}
            }
            
        # 3. 事件相关
        if "EVENTS/ANALYSIS" in p:
            return db.get("events", {})
        if "EVENTS/LIST" in p:
            return {"recent_events": db.get("events", {}).get("recent", [])}

        return {"error": "API Path Mismatch", "path": path}

processor = DataProcessor()

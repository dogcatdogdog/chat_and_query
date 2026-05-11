import json
import os
from typing import Dict, Any, List

class MockAPI:
    def __init__(self, pool_path: str = "data/v1.1/resource_pool.json"):
        self.pool_path = pool_path
        self.pool = self._load_pool()

    def _load_pool(self) -> Dict[str, Any]:
        if not os.path.exists(self.pool_path):
            return {}
        with open(self.pool_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _filter(self, data_list: List[Dict], params: Dict) -> List[Dict]:
        """通用的属性过滤器，模拟后端条件查询"""
        result = data_list
        for key, value in params.items():
            if value is not None:
                # 支持简单的 key=value 匹配
                result = [item for item in result if str(item.get(key)).lower() == str(value).lower()]
        return result

    def call(self, api_name: str, params: Dict = {}) -> Any:
        method_name = f"api_{api_name}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(params)
        return {"error": f"API {api_name} not implemented", "code": 404}

    # --- 1. get_device_list ---
    def api_get_device_list(self, params):
        return self._filter(self.pool.get("devices", []), params)

    # --- 2. get_device_detail ---
    def api_get_device_detail(self, params):
        sn = params.get("id") or params.get("sn")
        for d in self.pool.get("devices", []):
            if d["id"] == sn: return d
        return {"error": "Device not found"}

    # --- 3. get_airport_list ---
    def api_get_airport_list(self, params):
        return self._filter(self.pool.get("airports", []), params)

    # --- 4. get_mission_list ---
    def api_get_mission_list(self, params):
        return self._filter(self.pool.get("missions", []), params)

    # --- 4.1 get_mission_stats ---
    def api_get_mission_stats(self, params):
        missions = self.pool.get("missions", [])
        total = len(missions)
        success = len([m for m in missions if m.get("status") == "COMPLETED"])
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": f"{(success/total*100):.1f}%" if total > 0 else "0%",
            "data": missions # 同时也返回明细，方便 responder 分析
        }

    # --- 5. get_flight_records ---
    def api_get_flight_records(self, params):
        return self._filter(self.pool.get("flight_records", []), params)

    # --- 6. get_event_list ---
    def api_get_event_list(self, params):
        return self._filter(self.pool.get("events", []), params)

    # --- 7. get_workorder_list ---
    def api_get_workorder_list(self, params):
        return self._filter(self.pool.get("workorders", []), params)

    # --- 8. trigger_menu ---
    def api_trigger_menu(self, params):
        return {"status": "success", "menuId": params.get("menuId")}

mock_api = MockAPI()

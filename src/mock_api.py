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

    # --- 5. get_mission_stats ---
    def api_get_mission_stats(self, params):
        m = self.pool.get("missions", [])
        return {"total": len(m), "running": len([x for x in m if x["status"] == "RUNNING"])}

    # --- 6. get_route_list ---
    def api_get_route_list(self, params):
        return self._filter(self.pool.get("routes", []), params)

    # --- 7. get_flight_records ---
    def api_get_flight_records(self, params):
        return self._filter(self.pool.get("flight_records", []), params)

    # --- 8. get_flight_stats ---
    def api_get_flight_stats(self, params):
        recs = self.pool.get("flight_records", [])
        return {"totalSorties": sum(r["sorties"] for r in recs), "totalDuration": sum(r["duration"] for r in recs)}

    # --- 9. get_event_list ---
    def api_get_event_list(self, params):
        return self._filter(self.pool.get("events", []), params)

    # --- 10. get_event_stats ---
    def api_get_event_stats(self, params):
        evs = self.pool.get("events", [])
        return {"critical": len([e for e in evs if e["type"] == "CRITICAL"]), "total": len(evs)}

    # --- 11. get_report_list ---
    def api_get_report_list(self, params):
        return self._filter(self.pool.get("reports", []), params)

    # --- 12. get_report_summary ---
    def api_get_report_summary(self, params):
        rid = params.get("id")
        for r in self.pool.get("reports", []):
            if r["id"] == rid: return r
        return {"error": "Report not found"}

    # --- 13. get_workorder_list ---
    def api_get_workorder_list(self, params):
        return self._filter(self.pool.get("workorders", []), params)

    # --- 14. get_workorder_stats ---
    def api_get_workorder_stats(self, params):
        wos = self.pool.get("workorders", [])
        return {"unassigned": len([w for w in wos if w["status"] == "UNASSIGNED"]), "total": len(wos)}

    # --- 15. get_algorithm_list ---
    def api_get_algorithm_list(self, params):
        return self._filter(self.pool.get("algorithms", []), params)

    # --- 16. get_analytics_overview ---
    def api_get_analytics_overview(self, params):
        return self.pool.get("analytics", {}).get("overview")

    # --- 17. get_analytics_trends ---
    def api_get_analytics_trends(self, params):
        return self.pool.get("analytics", {}).get("trends")

    # --- 18. get_video_list ---
    def api_get_video_list(self, params):
        return self._filter(self.pool.get("media", {}).get("videos", []), params)

    # --- 19. get_photo_list ---
    def api_get_photo_list(self, params):
        return self._filter(self.pool.get("media", {}).get("photos", []), params)

    # --- 20. get_geofence_list ---
    def api_get_geofence_list(self, params):
        return self._filter(self.pool.get("geofences", []), params)

    # --- 21. get_flyarea_list ---
    def api_get_flyarea_list(self, params):
        return self._filter(self.pool.get("flyareas", []), params)

    # --- 22. get_entity_list ---
    def api_get_entity_list(self, params):
        return self._filter(self.pool.get("entities", []), params)

    # --- 23. get_entity_detail ---
    def api_get_entity_detail(self, params):
        eid = params.get("id")
        for e in self.pool.get("entities", []):
            if e["id"] == eid: return e
        return {"error": "Entity not found"}

    # --- 24. trigger_menu ---
    def api_trigger_menu(self, params):
        return {"status": "success", "menuId": params.get("menuId")}

mock_api = MockAPI()

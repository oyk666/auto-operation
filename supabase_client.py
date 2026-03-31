import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Use a local JSON file for storage to bypass Supabase login requirements
LOCAL_STORAGE_FILE = "automation_data.json"

class SupabaseManager:
    """Mocked Manager that uses local storage to bypass login requirements"""
    def __init__(self):
        self._ensure_storage_exists()
        self.current_user = self.get_current_user()

    def _ensure_storage_exists(self):
        if not os.path.exists(LOCAL_STORAGE_FILE):
            with open(LOCAL_STORAGE_FILE, 'w') as f:
                json.dump({"operations": [], "logs": []}, f)

    def _read_storage(self) -> Dict[str, Any]:
        try:
            with open(LOCAL_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {"operations": [], "logs": []}

    def _write_storage(self, data: Dict[str, Any]):
        with open(LOCAL_STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        return {"success": True, "user": {"id": "guest", "email": "guest@local"}}

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        return {"success": True, "user": {"id": "guest", "email": "guest@local"}}

    def sign_out(self) -> bool:
        return True

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Always return a guest user to bypass login checks"""
        return type('obj', (object,), {'id': 'guest', 'email': 'Guest User'})()

    def save_operation(self, name: str, description: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Save new operation locally"""
        try:
            data = self._read_storage()
            operation_id = str(uuid.uuid4())
            
            operation = {
                "id": operation_id,
                "user_id": "guest",
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "actions": actions
            }
            
            data["operations"].append(operation)
            self._write_storage(data)
            
            return {"success": True, "operation_id": operation_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_operation(self, operation_id: str, name: str, description: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update existing operation locally"""
        try:
            data = self._read_storage()
            found = False
            for op in data["operations"]:
                if op["id"] == operation_id:
                    op["name"] = name
                    op["description"] = description
                    op["actions"] = actions
                    op["updated_at"] = datetime.now().isoformat()
                    found = True
                    break
            
            if not found:
                return {"success": False, "error": "Operation not found"}
                
            self._write_storage(data)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_operations(self) -> List[Dict[str, Any]]:
        """Get all operations from local storage"""
        try:
            data = self._read_storage()
            return data["operations"]
        except Exception as e:
            print(f"Get operations error: {str(e)}")
            return []

    def get_operation_with_actions(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation with its actions from local storage"""
        try:
            data = self._read_storage()
            for op in data["operations"]:
                if op["id"] == operation_id:
                    return op
            return None
        except Exception as e:
            print(f"Get operation error: {str(e)}")
            return None

    def delete_operation(self, operation_id: str) -> Dict[str, Any]:
        """Delete operation locally"""
        try:
            data = self._read_storage()
            data["operations"] = [op for op in data["operations"] if op["id"] != operation_id]
            self._write_storage(data)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def log_execution(self, operation_id: str, batch_item: str, status: str, error_message: str = "") -> Dict[str, Any]:
        """Log execution event locally"""
        try:
            data = self._read_storage()
            log_id = str(uuid.uuid4())
            log_data = {
                "id": log_id,
                "operation_id": operation_id,
                "user_id": "guest",
                "batch_item": batch_item,
                "status": status,
                "error_message": error_message,
                "started_at": datetime.now().isoformat()
            }
            data["logs"].append(log_data)
            self._write_storage(data)
            return {"success": True, "log_id": log_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_execution_logs(self, operation_id: str) -> List[Dict[str, Any]]:
        """Get execution logs for operation locally"""
        try:
            data = self._read_storage()
            logs = [log for log in data["logs"] if log["operation_id"] == operation_id]
            return sorted(logs, key=lambda x: x["started_at"], reverse=True)
        except Exception as e:
            print(f"Get logs error: {str(e)}")
            return []

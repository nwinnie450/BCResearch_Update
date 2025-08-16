"""
Persistent schedule storage with JSON backend
"""
import json
import os
import uuid
from typing import Dict, List

STORE_PATH = "data/schedules.json"

def _ensure_dir():
    """Ensure data directory exists"""
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)

def load_schedules() -> List[Dict]:
    """Load all schedules from persistent storage"""
    if not os.path.exists(STORE_PATH):
        return []
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_schedules(items: List[Dict]) -> None:
    """Save schedules to persistent storage with atomic write"""
    _ensure_dir()
    tmp = STORE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, STORE_PATH)

def new_schedule_id() -> str:
    """Generate unique schedule ID"""
    return str(uuid.uuid4())

def get_schedule_by_id(schedule_id: str) -> Dict:
    """Get single schedule by ID"""
    schedules = load_schedules()
    for sched in schedules:
        if sched.get("id") == schedule_id:
            return sched
    return None

def update_schedule(schedule_id: str, updates: Dict) -> bool:
    """Update specific schedule and save"""
    schedules = load_schedules()
    for i, sched in enumerate(schedules):
        if sched.get("id") == schedule_id:
            schedules[i].update(updates)
            save_schedules(schedules)
            return True
    return False

def delete_schedule(schedule_id: str) -> bool:
    """Delete schedule by ID"""
    schedules = load_schedules()
    for i, sched in enumerate(schedules):
        if sched.get("id") == schedule_id:
            schedules.pop(i)
            save_schedules(schedules)
            return True
    return False
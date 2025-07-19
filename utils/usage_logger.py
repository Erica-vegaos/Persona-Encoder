import os
import json
from datetime import datetime

LOG_FILE_PATH = "/data/logs/usage_log.jsonl"  # Fly.io volume 掛載點

def log_usage(event_name: str):
    log_entry = {
        "event": event_name,
        "timestamp": datetime.now().isoformat()
    }

    # 記錄至 session_state
    if "usage_log" not in st.session_state:
        st.session_state["usage_log"] = []
    st.session_state["usage_log"].append(log_entry)

    # 寫入檔案（append 模式）
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to write log: {e}")

    # 顯示 console log（開發階段用）
    print(f"[LOG] {event_name} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

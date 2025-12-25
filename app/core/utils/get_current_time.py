from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_time():
    updated_time_bd = datetime.now(ZoneInfo("Asia/Dhaka"))
    updated_time_bd = updated_time_bd.replace(tzinfo=None)
    return updated_time_bd
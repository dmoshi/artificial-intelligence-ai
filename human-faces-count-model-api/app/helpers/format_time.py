from datetime import datetime, timezone, timedelta

def time_passed_str(start: datetime, end: datetime) -> str:

    # Convert to UTC+3
    start_utc = start.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=3)))
    end_utc = end.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=3)))

    diff = end_utc - start_utc
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds}s ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago"
    else:
        days = seconds // 86400
        return f"{days}d ago"
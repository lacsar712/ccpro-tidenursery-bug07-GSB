from datetime import datetime, timedelta, timezone

# 台账统一按东八区（北京时间）划界；汇总卡与列表过滤必须共用本模块函数，
# 不得各自再实现一套时间窗，否则两边数字会漂移。
LOCAL_TZ = timezone(timedelta(hours=8))


def as_local_aware(value: datetime) -> datetime:
    """把投喂时刻统一成带时区的 UTC 时间。

    前端发来的带偏移量时间（如 2026-09-23T18:00:00+08:00 / ...Z）按其偏移解释；
    极少数不带时区信息的时间按东八区解释，而不是按 UTC 静默误读。
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=LOCAL_TZ)
    return value.astimezone(timezone.utc)


def local_window_start(days: int, now: datetime | None = None) -> datetime:
    """东八区近 N 日的起始时刻（含），返回带 UTC 时区的 datetime，可直接与库中时间比较。

    口径为「现在往前 N*24 小时」，与列表 lastDays=N 的过滤完全一致：
    同一条记录要么同时出现在汇总与列表里，要么都不出现。
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=LOCAL_TZ)
    local_now = now.astimezone(LOCAL_TZ)
    start_local = local_now - timedelta(days=days)
    return start_local.astimezone(timezone.utc)

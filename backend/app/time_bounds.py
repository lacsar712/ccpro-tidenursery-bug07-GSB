from datetime import datetime, timedelta, timezone
from typing import Optional

# 全场统一按东八区给“近 N 日”划界,列表过滤与看板汇总必须共用本模块,
# 任何一边都不得另写窗口算法,否则两处千克数会漂移。
LOCAL_TZ = timezone(timedelta(hours=8))


def rolling_window_start(days: int, now: Optional[datetime] = None) -> datetime:
    """近 N 日滚动窗口的起点(含边界),以 UTC aware datetime 返回。

    取东八区当前时刻减去 N 天,再换算到 UTC。投喂记录按 UTC 存储,
    调用方统一用 ``FeedEvent.fed_at >= rolling_window_start(n)`` 过滤,
    汇总 SUM 与列表行即为同一批数据。
    """
    ref = now if now is not None else datetime.now(LOCAL_TZ)
    if ref.tzinfo is None:
        #  naive 输入按东八区本地时间解释,而不是按服务器/UTC 猜测
        ref = ref.replace(tzinfo=LOCAL_TZ)
    else:
        ref = ref.astimezone(LOCAL_TZ)
    return (ref - timedelta(days=days)).astimezone(timezone.utc)


def as_utc(value: datetime) -> datetime:
    """把投喂时刻归一为 UTC aware:naive 值按东八区解释。"""
    if value.tzinfo is None:
        value = value.replace(tzinfo=LOCAL_TZ)
    return value.astimezone(timezone.utc)

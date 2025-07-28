from datetime import datetime
from typing import List

from croniter import croniter


def preview_next_runs(cron_expression: str, count: int = 10) -> List[str]:
    """Return the next `count` run times for the given cron expression."""
    now = datetime.now()
    itr = croniter(cron_expression, now)
    return [itr.get_next(datetime).isoformat(sep=' ') for _ in range(count)]

import datetime
from typing import Optional


def generate_random_date(start_datetime: Optional[datetime] = None,
                         end_datetime: Optional[datetime] = None) -> datetime.date:
    import random
    from datetime import datetime, timedelta
    start_date = start_datetime or datetime(1920, 1, 1)
    end_date = end_datetime or datetime.now()
    random_seconds = random.randrange(0, int((end_date - start_date).total_seconds()))
    random_datetime = start_date + timedelta(seconds=random_seconds)
    return random_datetime.date()

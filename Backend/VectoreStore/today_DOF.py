import asyncio
from datetime import datetime

from deap_main import ingest_date


POLL_INTERVAL_SECONDS = 24 * 60 * 60


async def monitor_today() -> None:
    while True:
        date_value = datetime.now().strftime("%d-%m-%Y")
        await asyncio.to_thread(ingest_date, date_value)
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(monitor_today())

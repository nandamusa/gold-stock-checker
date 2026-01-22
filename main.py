import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from config import LOCATION_MAP
from extractor import Extractor
from notifier import Notifier
from exceptions import AppError
from logger import log


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(AppError),
    before_sleep=before_sleep_log(log, logging.WARNING)
)
async def process_single_location(sem: asyncio.Semaphore, notifier: Notifier, loc_name: str, loc_id: str):
    async with sem:
        extractor = Extractor() 
        try:
            data = await extractor.process_location(loc_name, loc_id)
            if data and data['products']:
                await notifier.send_stock_update(data['key'], data['display_name'], data['products'])
        finally:
            await extractor.close()

async def main():
    log.info("system.start")
    
    notifier = Notifier()
    sem = asyncio.Semaphore(3)
    tasks = []

    for loc_name, loc_id in LOCATION_MAP.items():
        task = asyncio.create_task(
            process_single_location(sem, notifier, loc_name, loc_id)
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        loc_name = list(LOCATION_MAP.keys())[i]
        
        if isinstance(result, Exception):
            log.error(f"Synchronization failed for {loc_name} after multiple attempts.", error=str(result))
        else:
            log.info(f"Successfully processed node: {loc_name}")

    success_count = sum(1 for r in results if not isinstance(r, Exception))
    fail_count = len(results) - success_count

    log.info("system.finish", total=len(results), success=success_count, failed=fail_count)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
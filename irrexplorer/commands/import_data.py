import asyncio
import logging
import os
from datetime import datetime, timezone

from irrexplorer.backends.bgp import BGPImporter
from irrexplorer.backends.metadata import update_last_data_import
from irrexplorer.backends.registro import RegistroRirImporter
from irrexplorer.backends.rirstats import RIRStatsImporter
from irrexplorer.debugging import install_sigusr1_handler
from irrexplorer.settings import IMPORT_TIMEOUT, RIRSTATS_URL

logger = logging.getLogger(__name__)


def configure_process():  # pragma: no cover
    """
    Set up logging and the SIGUSR1 stack dump handler.
    """
    # Only our own loggers go to INFO: at that level the database library
    # logs the DATABASE_URL, which may hold a password.
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("irrexplorer").setLevel(logging.INFO)
    install_sigusr1_handler()


async def main():
    """
    Run an import for all backends with local data.
    All imports are run "simultaneously" (one CPU, but async)
    """
    import_time = datetime.now(tz=timezone.utc)
    tasks = [RIRStatsImporter(rir).run_import() for rir in RIRSTATS_URL]
    tasks.append(RegistroRirImporter().run_import())
    tasks.append(BGPImporter().run_import())
    try:
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=IMPORT_TIMEOUT)
    except asyncio.TimeoutError:
        # we can't cancel the thread, so abort the whole process
        # (with os._exit as sys.exit waits for the thread to finish)
        logger.error(f"import timed out after {IMPORT_TIMEOUT} seconds, exiting")
        logging.shutdown()
        os._exit(1)
    except Exception:
        # also abort hard: a parse thread may still be running
        logger.exception("import failed, exiting")
        logging.shutdown()
        os._exit(1)
    logger.info("import completed")
    await update_last_data_import(import_time)


if __name__ == "__main__":
    configure_process()
    asyncio.run(main())

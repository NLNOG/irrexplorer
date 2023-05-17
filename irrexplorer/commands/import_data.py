import asyncio
from datetime import datetime, timezone

from irrexplorer.backends.bgp import BGPImporter
from irrexplorer.backends.registro import RegistroRirImporter
from irrexplorer.backends.metadata import update_last_data_import
from irrexplorer.backends.rirstats import RIRStatsImporter
from irrexplorer.state import RIR


async def main():
    """
    Run an import for all backends with local data.
    All imports are run "simultaneously" (one CPU, but async)
    """
    import_time = datetime.now(tz=timezone.utc)
    tasks = []
    for rir in RIR:
        if rir == RIR.REGISTROBR:
            tasks.append(RegistroRirImporter().run_import())
        else:
            tasks.append(RIRStatsImporter(rir).run_import())
    tasks.append(BGPImporter().run_import())
    await asyncio.gather(*tasks)
    await update_last_data_import(import_time)


if __name__ == "__main__":
    asyncio.run(main())

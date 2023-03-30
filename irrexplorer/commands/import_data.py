import asyncio

from irrexplorer.backends.bgp import BGPImporter
from irrexplorer.backends.registro import RegistroImporter
from irrexplorer.backends.rirstats import RIRStatsImporter
from irrexplorer.state import RIR


async def main():
    """
    Run an import for all backends with local data.
    All imports are run "simultaneously" (one CPU, but async)
    """
    tasks = []
    for rir in RIR:
        if rir == RIR.REGISTROBR:
            tasks.append(RegistroImporter().run_import())
        else:
            tasks.append(RIRStatsImporter(rir).run_import())
    tasks.append(BGPImporter().run_import())
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

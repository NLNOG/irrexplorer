import asyncio

from irrexplorer.backends.rirstats import RIRStatsImporter
from irrexplorer.backends.bgp import BGPImporter
from irrexplorer.state import RIR


async def main():
    tasks = []
    for rir in RIR:
        tasks.append(RIRStatsImporter(rir).run_import())
    tasks.append(BGPImporter().run_import())
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

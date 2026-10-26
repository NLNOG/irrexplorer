import asyncio

import pytest

from irrexplorer.commands import import_data

pytestmark = pytest.mark.asyncio


class StubImporter:
    def __init__(self, *args):
        pass

    async def run_import(self):
        pass


class HangingImporter(StubImporter):
    async def run_import(self):
        await asyncio.sleep(10)


async def test_main_timeout_exits(monkeypatch):
    def fake_exit(status):
        raise SystemExit(status)

    monkeypatch.setattr(import_data.os, "_exit", fake_exit)
    monkeypatch.setattr(import_data, "RIRStatsImporter", StubImporter)
    monkeypatch.setattr(import_data, "RegistroRirImporter", StubImporter)
    monkeypatch.setattr(import_data, "BGPImporter", HangingImporter)
    monkeypatch.setattr(import_data, "IMPORT_TIMEOUT", 0.05)

    # main() must not return: it exits rather than wait for the thread
    with pytest.raises(SystemExit) as exc_info:
        await import_data.main()
    assert exc_info.value.code == 1

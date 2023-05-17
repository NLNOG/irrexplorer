from datetime import datetime

from databases import Database

from irrexplorer.settings import DATABASE_URL
from irrexplorer.storage import tables


async def update_last_data_import(import_time: datetime):
    async with Database(DATABASE_URL) as database:
        async with database.transaction():
            await database.execute(tables.last_data_import.delete())
            await database.execute(
                tables.last_data_import.insert().values(last_data_import=import_time)
            )


async def get_last_data_import() -> datetime:
    async with Database(DATABASE_URL) as database:
        return await database.execute(tables.last_data_import.select())

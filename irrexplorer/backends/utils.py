import aiohttp

from irrexplorer.exceptions import ImporterException


async def retrieve_url_text(url: str):
    """
    Retrieve `url` and return the text in the response.
    Raises ImporterException if the response status is not 200.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ImporterException(f"Failed import from {url}: status {response.status}")
            return await response.text()

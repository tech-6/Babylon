import logging
import os
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from disnake import ApplicationCommandInteraction, Attachment, Event
from disnake.ext import commands

from librarian.dependable.bot_overload import InteractionBot


class Upload(commands.Cog):
    def __init__(self, bot: InteractionBot):
        self.logger = logging.getLogger(__name__)
        self._library_cache: tuple[dict[str, int], datetime] = ({},
                                                                datetime.min)
        self.bot = bot
        self.http_session: aiohttp.ClientSession | None = None

    @commands.Cog.listener(Event.ready)
    async def on_ready(self):
        self.http_session = aiohttp.ClientSession(
            headers={'User-Agent': self.bot.user_agent}
        )

    @commands.slash_command()
    async def upload(self, file: Attachment, library: str,
        interaction: ApplicationCommandInteraction):
        print(file.url)
        print(file.content_type)

        await interaction.response.defer()
        file_content = (await self.http_session.request('GET', file.url, allow_redirects=True, headers={'User-Agent': self.bot.user_agent})).content

        print(await self._libraries)
        if library not in (await self._libraries).keys():
            return await interaction.edit_original_response(content="Library not found.")
        try:
            os.makedirs(f'/libraries/{library.lower()}/userupload', exist_ok=True)


            with open(f'/libraries/{library.lower()}/userupload/{file.filename}', 'xb') as f:
                async for b, _ in file_content.iter_chunks():
                    f.write(b)

        except Exception as e:
            return await interaction.edit_original_response(content=f"Error uploading {file.filename}: {e}")
        return await interaction.edit_original_response(content=f"Successfully uploaded {file.filename} to {library}.")

    @upload.autocomplete('library')
    async def library_autocomplete(self,
        _: ApplicationCommandInteraction,
        string: str):
        return [_ for _ in (await self._libraries).keys() if
                string.lower() in _.lower()]

    @property
    async def _libraries(self) -> dict[str, int]:
        if datetime.now() < self._library_cache[1]:
            self.logger.debug("Module Cache: HIT")
            return self._library_cache[0]
        self.logger.debug("Module Cache: MISS")
        libraries = {}

        libraries_response = await self.http_session.request(
            'GET',
            f'{self.bot.config.get('kavita_base_url')}/api/Library/libraries',
            headers={'Authorization': f'Bearer {await self.get_jwt()}'}

        )
        libraries_available: list[dict[str, Any]] = await libraries_response.json()

        for library in libraries_available:
            libraries[library['name']] = library['id']
        self._library_cache = (libraries,
                               datetime.now() + timedelta(seconds=30))
        return libraries

    async def get_jwt(self):
        key = self.bot.config.get('kavita_api_key')
        if self.http_session is None:
            raise RuntimeError("HTTP Session not initialized.")
        async with self.http_session.request('POST',
                                             f'{self.bot.config.get('kavita_base_url')}/api/Plugin/authenticate',
                                             params={
                                                 'apiKey': key,
                                                 'pluginName': 'librarian'
                                             }) as resp:
            resp.raise_for_status()
            token = (await resp.json())
            print(token)
            return token['token']

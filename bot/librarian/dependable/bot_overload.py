from typing import Optional

import disnake
import disnake.ext.commands as dc
from disnake import ClientException
from disnake.ext.commands import CommandError, Cog

from librarian.dependable.configuration import Configuration
from librarian.dependable.paste import Paste


class InteractionBot(dc.InteractionBot):
    version: str | None = None
    user_agent: str | None = None

    def __init__(self, config: Configuration, *args, **kwargs):
        self._loaded_cogs: list[str] = []
        self.config: Configuration = config

        self.paste = Paste(self.config, self.user_agent)

        intents = disnake.Intents.default()
        super().__init__(*args, **kwargs, intents=intents)
        # self.add_listener(self.on_ready, Event.ready)

    async def connect(
        self, *, reconnect: bool = True,
        ignore_session_start_limit: bool = False
    ) -> None:
        self.user_agent = (
            self.config.get('user_agent'))
        self.paste.user_agent = self.user_agent
        await super().connect(
            reconnect=reconnect,
            ignore_session_start_limit=ignore_session_start_limit
        )

    def add_cog(self, cog: dc.Cog, *, override: bool = False) -> None:
        try:
            super().add_cog(cog, override=override)
        except TypeError:
            raise TypeError("cog is not a subclass of Cog.")
        except CommandError:
            raise CommandError()
        except ClientException:
            raise ClientException()
        else:
            if cog.qualified_name not in self._loaded_cogs:
                self._loaded_cogs.append(cog.qualified_name)

    def remove_cog(self, name: str) -> Optional[Cog]:
        cog = super().remove_cog(name)
        if cog is not None:
            self._loaded_cogs.remove(cog.qualified_name)
        return cog

    @property
    def loaded_cogs(self) -> list[str]:
        return self._loaded_cogs

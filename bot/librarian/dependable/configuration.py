import copy
import logging
import os
import pickle
from os import environ
from pathlib import Path

from typing_extensions import Any

# from koor.dependable.bot_overload import InteractionBot
from librarian.dependable.exceptions import BlockedConfigurationKeyException


logger = logging.getLogger(__name__)


class Configuration(dict):
    # _bot: InteractionBot | None = None

    # Luckperms Cog
    luckperms_base_url: str | None
    luckperms_api_username: str | None
    luckperms_api_password: str | None

    # MC Profile Cog
    mcprofile_api_key: str | None

    # Paste Cog
    paste_api_url = str | None
    paste_frontend_url = str | None

    # Welcome Cog
    # Server, Channel, Message
    welcome_server_messages: list[tuple[int, int, str]] | None

    # Hosepipe Cog
    hosepipe_servers: list[tuple[int, int, int, int | None]] | None
    hosepipe_ignored: list[int] | None

    # BotStatus Cog
    botstatus_activity: list[str] | None
    botstatus_status: str | None

    # Safety!
    censored_keys: list[str] = [
        'luckperms_api_password',
        'mcprofile_api_key'
    ]

    def __str__(self) -> str:
        dictionary = self.__dict__.copy()
        for key in dictionary.keys():
            if key in self.censored_keys:
                dictionary[key] = '******'

        return str(dictionary)

    def show(self, key: str) -> str | None:
        if key in self.censored_keys:
            raise BlockedConfigurationKeyException(key)
        return self.get(key)

    def set(self, key: str, value: Any):
        self[key] = value
        # self._bot.dispatch("configuration_set", key=key, value=value)

    def configuration_get_key(self, key: str) -> Any | None:
        return self.get(key)

    def censored_copy(self):
        copied_configuration = copy.deepcopy(self)
        for key in copied_configuration.keys():
            if key in copied_configuration.censored_keys:
                copied_configuration[key] = '******'
        return copied_configuration

    def save(self):
        path: Path = Path(os.environ.get('CONFIG_DIR')) / 'koor.dat'
        os.makedirs(os.path.dirname(path), exist_ok=True)

        config = copy.deepcopy(self)
        config._bot = None

        with open(path, 'wb') as file:
            # noinspection PyTypeChecker
            pickler = pickle.Pickler(file, protocol=pickle.HIGHEST_PROTOCOL)
            pickler.dump(config)

    @staticmethod
    def from_env():
        paste_api_url = environ.get('PASTE_API_URL')
        paste_frontend_url = environ.get('PASTE_FRONTEND_URL')
        user_agent = environ.get('USER_AGENT')

        return Configuration(
            # _bot=bot,
            paste_api_url=paste_api_url,
            paste_frontend_url=paste_frontend_url,
            user_agent=user_agent,
            botstatus_activity=[],
            censored_keys=[]
        )

    @staticmethod
    def from_stored():
        path: Path = Path(os.environ.get('CONFIG_DIR')) / 'koor.dat'
        with open(path, 'rb') as file:
            configuration: Configuration = pickle.Unpickler(file).load()
            return configuration

from enum import Enum

from aiohttp import ClientSession

from librarian.dependable.exceptions import PasteFailedException
from librarian.dependable.configuration import Configuration


class TextTypes(str, Enum):
    PLAIN = 'text/plain'
    LOG = 'text/log'

    YAML = 'text/yaml'
    JSON = 'application/json'
    XML = 'application/xml'
    INI = 'text/ini'

    JAVA = 'text/java'
    JAVASCRIPT = 'application/javascript'
    TYPESCRIPT = 'text/typescript'
    PYTHON = 'text/python'
    KOTLIN = 'text/kotlin'
    SCALA = 'text/scala'
    CPP = 'text/cpp'
    CSHARP = 'text/csharp'
    SHELL = 'text/shell'
    RUBY = 'text/ruby'
    RUST = 'text/rust'
    SQL = 'text/sql'
    GO = 'text/go'
    LUA = 'text/lua'
    SWIFT = 'text/swift'
    C = 'text/c'

    HTML = 'text/html'
    CSS = 'text/css'
    SCSS = 'text/scss'
    PHP = 'text/php'
    GRAPHQL = 'text/graphql'

    DIFF = 'text/diff'
    DOCKERFILE = 'text/dockerfile'
    MARKDOWN = 'text/markdown'
    PROTO = 'text/proto'

    def __str__(self):
        return self.value


class Paste:
    def __init__(self, config: Configuration, user_agent: str | None = None):
        self.client: ClientSession | None = None
        self.config = config
        self._user_agent: str | None = user_agent
        # self.user_agent = user_agent

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str | None):
        self._user_agent = value

    async def _setup_http_session(self):
        self.client = ClientSession()

    async def paste(self, content: str | bytes,
        content_type: str | TextTypes = 'text/plain') -> str:
        if self.client is None:
            await self._setup_http_session()

        paste_api_url: str | None = self.config.get('paste_api_url')

        print(paste_api_url)
        print(content_type)

        http_client = self.client
        async with http_client.post(
            paste_api_url + '/post',
            headers={
                'Content-Type': str(content_type),
                'User-Agent': self.user_agent
            },
            data=content,
        ) as post:
            json: dict[str, str] = await post.json()
            key = json.get('key')
            if key is None:
                raise PasteFailedException
            return f'{self.config.get('paste_frontend_url')}/{key}'

import importlib
import json
import logging
from datetime import datetime, timedelta, UTC
from pkgutil import iter_modules
from traceback import format_exc

from disnake import ApplicationCommandInteraction, Embed, Color
from disnake.ext import commands
from disnake.ext.commands import Cog, Context

from librarian.dependable.bot_overload import InteractionBot
from librarian.dependable.exceptions import KoorModuleLoadException
from librarian.dependable.paste import TextTypes


def _snake_case_to_camel_case(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


async def _owner_check(ctx: Context) -> bool:
    if ctx.author.id != ctx.bot.owner.id:
        await ctx.send('# You dont own me!')
        return False
    return True


class Management(commands.Cog):
    def __init__(self, bot: InteractionBot):
        self.bot = bot
        self._module_cache: tuple[list[str], datetime] = ([], datetime.min)
        self.logger = logging.getLogger(__name__)

    @commands.slash_command(guild_ids=[1080640807951929425])
    async def management(self, interaction: ApplicationCommandInteraction):
        pass

    @commands.check(_owner_check)
    @management.sub_command()
    async def reload_module(self,
        interaction: ApplicationCommandInteraction,
        module: str,
        ephemeral: bool = True):
        """
        Reload a module in the bot

        Parameters
        ----------
        module: The module to reload
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        """

        cog: Cog | None = None
        await interaction.response.send_message(
            f'Attempting to reload module `{module}`',
            ephemeral=ephemeral)
        try:
            cog = self.bot.remove_cog(module)
        except Exception as _:
            _original_response = await interaction.original_response()
            await _original_response.edit(
                content=f'Unable to unload module: {module} \n'
                        f'exception: ```py\n{format_exc()}```')
        if cog is None:
            _original_response = await interaction.original_response()
            await _original_response.edit(
                content=f'Module `{module}` not currently loaded. '
                        f'Attempting to load!'
            )

        else:
            _original_response = await interaction.original_response()
            await _original_response.edit(
                content=f'Module `{module}` successfully unloaded. '
                        f'Attempting to reload!'
            )

        try:
            importlib.invalidate_caches()
            cog_module = importlib.import_module(
                f'librarian.cogs.{module.lower()}')

            cog_to_be_loaded: Cog = getattr(cog_module, module)(self.bot)
            self.bot.add_cog(cog_to_be_loaded)

        except ModuleNotFoundError as _:
            _original_response = await interaction.original_response()
            return await _original_response.edit(
                content=f'Unable to load module: `{module}`\n'
                        f'# That module does not exist!')
        except KoorModuleLoadException as _:
            _original_response = await interaction.original_response()
            return await _original_response.edit(
                content=f'Unable to load module: `{module}` \n'
                        f'exception: ```py\n{format_exc()}```')

        _original_response = await interaction.original_response()
        return await _original_response.edit(
            content=f'Module `{module}` successfully reloaded.'
        )

    @commands.check(_owner_check)
    @management.sub_command()
    async def unload_module(self,
        interaction: ApplicationCommandInteraction,
        module: str,
        ephemeral: bool = True):
        """
        Unloads a module from the bot

        Parameters
        ----------
        module: The module to unload
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        """

        try:
            cog = self.bot.remove_cog(module)

        except Exception as _:
            return await interaction.response.send_message(
                f'Unable to unload module: `{module}`\n'
                f'Exception: ```py\n{format_exc()}```',
                ephemeral=ephemeral
            )

        if cog is None:
            return await interaction.response.send_message(
                f'Module `{module}` not loaded.'
            )

        return await interaction.response.send_message(
            f'Module `{module}` successfully unloaded.'
        )

    @unload_module.autocomplete('module')
    @reload_module.autocomplete('module')
    async def module_autocomplete(self,
        _: ApplicationCommandInteraction,
        string: str):
        return [_snake_case_to_camel_case(module) for module in self._modules if
                string.lower() in module]

    @management.sub_command(name='version')
    async def management_version_stub(self,
        interaction: ApplicationCommandInteraction,
        ephemeral: bool = True):
        """
        Get currently running version of the bot.

        Parameters
        ----------
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        """
        return await self.version_command(
            interaction,
            ephemeral=ephemeral,
        )

    @commands.slash_command(name='about')
    async def about_stub(self,
        interaction: ApplicationCommandInteraction,
        ephemeral: bool = True):
        """
        Get currently running version of the bot.

        Parameters
        ----------
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        """
        return await self.version_command(
            interaction,
            ephemeral=ephemeral,
        )

    async def version_command(self,
        interaction: ApplicationCommandInteraction,
        ephemeral: bool = True):

        await interaction.response.defer(ephemeral=ephemeral)

        embed = Embed(
            description=f'You are using Librarian',
            color=Color.purple(),

            url='https://github.com/tech_6/Babylon'
        )

        tech_user = await self.bot.getch_user(727950472266383380)

        embed.set_author(name=tech_user.display_name,
                         url='https://discord.com/users/727950472266383380',
                         icon_url=tech_user.avatar.url)
        embed.set_footer(text='made with 🖤 by Lexie "Tech" Malina.',
                         icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        return await interaction.edit_original_response(embed=embed)

    @management.sub_command()
    async def status(self,
        interaction: ApplicationCommandInteraction,
        ephemeral: bool = True):
        """
        Shows current status of the bot.
        Parameters
        ----------
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        """

        loaded_modules = self.bot.loaded_cogs
        total_modules = self._modules
        ping = self.bot.latency

        embed = Embed(
            timestamp=datetime.now(UTC),
            color=Color.purple(),
        )

        embed.set_author(name=self.bot.user.display_name,
                         icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field('Ping', f'{int(ping * 1000)}ms', inline=False)

        for total_module in total_modules:
            loaded: bool = False
            if _snake_case_to_camel_case(total_module) in loaded_modules:
                loaded = True
            embed.add_field(_snake_case_to_camel_case(total_module),
                            'Loaded' if loaded else "Not Loaded", )

        await interaction.response.send_message(embed=embed,
                                                ephemeral=ephemeral)

    @commands.check(_owner_check)
    @management.sub_command()
    async def dump_config(self,
        interaction: ApplicationCommandInteraction,
        ephemeral: bool = True):
        """
        Dumps the currently running bot config

        Parameters
        ----------
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        """

        paste = self.bot.paste
        paste_url = await paste.paste(
            json.dumps(self.bot.config.censored_copy(), indent=4,
                       sort_keys=True),
            TextTypes.JSON)
        await interaction.response.send_message(
            f'{paste_url}',
            ephemeral=ephemeral
        )

    @commands.check(_owner_check)
    @management.sub_command()
    async def set_config(self,
        interaction: ApplicationCommandInteraction,
        key: str,
        value: str,
        ephemeral: bool = True):
        """
        Dumps the currently running bot config

        Parameters
        ----------
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        key: Where the value will be stored in the config.
        value: Value that will be entered into key.
        """

        value_json = '{"value": ' + value + '}'
        self.logger.info(f'Setting {key} to {value_json}')
        try:
            json_object = json.loads(value_json)
        except json.decoder.JSONDecodeError as e:
            self.logger.error(f'Could not decode JSON value {value_json}')
            embed = Embed(
                timestamp=datetime.now(UTC),
                color=Color.red(),
                title=f'Could not decode JSON value for {key}',
                description=f'{e.msg}',
            )

            embed.set_author(name=self.bot.user.display_name,
                             icon_url=self.bot.user.display_avatar.url)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            return await interaction.response.send_message(embed=embed,
                                                           ephemeral=ephemeral)

        self.bot.config.set(key, json_object.get('value'))

        embed = Embed(
            timestamp=datetime.now(UTC),
            color=Color.green(),
            title=f'Successfully set {key}',
        )

        embed.set_author(name=self.bot.user.display_name,
                         icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        return await interaction.response.send_message(embed=embed,
                                                       ephemeral=ephemeral)

    @commands.check(_owner_check)
    @management.sub_command()
    async def save_config(self,
        interaction: ApplicationCommandInteraction,
        ephemeral: bool = True):
        """
        Saves the currently running bot config to disk making it persistent.

        Parameters
        ----------
        ephemeral: Whether this message show to shown to all users.
        interaction: Interaction given from disnake
        """
        self.logger.info('Saving running bot config to disk.')
        self.bot.config.save()
        self.bot.dispatch('config_saved')
        return await interaction.response.send_message('Config saved.',
                                                       ephemeral=ephemeral)

    @set_config.autocomplete('key')
    async def config_autocomplete(self,
        _: ApplicationCommandInteraction,
        string: str):
        return [key for key in self._configuration_keys if
                key[0] != '_' and string.lower() in key]

    @property
    def _configuration_keys(self):
        return [key for key in self.bot.config.censored_copy().keys()]

    @property
    def _modules(self) -> list[str]:
        if datetime.now() < self._module_cache[1]:
            self.logger.debug("Module Cache: HIT")
            return self._module_cache[0]
        self.logger.debug("Module Cache: MISS")
        modules = [name for _, name, _ in iter_modules(['librarian/cogs'])]
        self._module_cache = (modules, datetime.now() + timedelta(seconds=30))
        return modules

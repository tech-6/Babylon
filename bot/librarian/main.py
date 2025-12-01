import logging
from os import environ

from disnake import Status, InteractionContextTypes

from librarian.cogs.upload import Upload
from librarian.cogs.management import Management
from librarian.dependable.bot_overload import InteractionBot
from librarian.dependable.configuration import Configuration


def main() -> int:
    logger = logging.getLogger('Librarian')
    logging.basicConfig(level=logging.INFO)

    config: Configuration | None = None

    try:
        config = Configuration.from_stored()
        logger.info(f'Configuration loaded from stored configuration')
    except FileNotFoundError:
        logger.info(
            f'Configuration not found from stored configuration, attempting to generate from environment')
        config = Configuration.from_env()
    finally:
        if config is None:
            raise EnvironmentError('No configuration found')
        logger.info('Configuration loaded.')

    discord_token = environ.get('DISCORD_TOKEN')
    if discord_token is None:
        logger.error('Missing DISCORD_TOKEN')
        logger.error('Exiting...')
        return 1

    bot = InteractionBot(config,
                         status=Status.dnd,
                         default_contexts=InteractionContextTypes(guild=True)
                         )

    bot.add_cog(Management(bot))
    bot.add_cog(Upload(bot))
    bot.run(discord_token)
    return 0


if __name__ == '__main__':
    main()

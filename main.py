import discord
from discord.ext import commands
from discord import app_commands
from config import DISCORD_TOKEN
import asyncio
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True  # Habilitar intents para conteúdo das mensagens
intents.dm_messages = True  # Habilitar intents para mensagens diretas
bot = commands.Bot(command_prefix='!', intents=intents)

# URL da imagem do bot, banner e informações adicionais
BOT_IMAGE_URL = 'https://i.imgur.com/ehY6NHg.png'  # Substitua pela URL da imagem do bot
BOT_BANNER_URL = 'https://i.imgur.com/e8n7zVS.jpeg'  # Substitua pela URL do banner
BOT_NAME = 'Miuki'
BOT_DESCRIPTION = 'Miuki é uma anjo caída com uma abordagem direta e sem filtros.\n\nMiuki é um bot para Geração e manipulação de imagem.'
BOT_STATUS = 'Dados com o Destino'

# Módulos a serem carregados
initial_extensions = [
    'modules.sdxlgen',
    'modules.sd1xgen',
    'modules.upscale',
    'modules.lorasmodels',
]

async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            logging.info(f'Loaded extension: {extension}')
        except Exception as e:
            logging.error(f'Failed to load extension {extension}: {e}')

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    await load_extensions()

    try:
        synced = await bot.tree.sync()
        logging.info(f'Synced {len(synced)} commands')
    except Exception as e:
        logging.error(f'Failed to sync commands: {e}')

    # Atualiza a presença do bot com uma imagem, descrição e status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=BOT_STATUS))

    # Adiciona uma mensagem de depuração para listar os comandos
    for command in bot.tree.get_commands():
        logging.info(f'Command: {command.name}, Description: {command.description}')

# Failsafe no caso de atraso ou ausência de módulos
async def failsafe_startup(retries=5, delay=10):
    attempt = 0
    while attempt < retries:
        try:
            await bot.start(DISCORD_TOKEN)
            return  # Se o bot iniciar com sucesso, sai da função
        except Exception as e:
            logging.error(f'Failed to start bot: {e}')
            attempt += 1
            if attempt < retries:
                logging.info(f'Retrying in {delay} seconds... (Attempt {attempt}/{retries})')
                await asyncio.sleep(delay)
            else:
                logging.error('Max retries reached. Exiting.')

if __name__ == '__main__':
    asyncio.run(failsafe_startup())

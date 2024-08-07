import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
from config import API_KEY
from .choices import style_preset_choices, sampler_choices

image_cache = {}
filter_active = True  # Filtro ativo por padrão
filter_words = []  # Lista de palavras filtradas

class ButtonView(discord.ui.View):
    def __init__(self, interaction, cache_key):
        super().__init__()
        self.interaction = interaction
        self.cache_key = cache_key

    @discord.ui.button(label="Deletar", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.interaction.user or interaction.user.guild_permissions.administrator:
            try:
                await interaction.message.delete()
                image_cache.pop(self.cache_key, None)
            except discord.Forbidden:
                await interaction.response.send_message('Não tenho permissão para deletar esta mensagem.', ephemeral=True)
        else:
            await interaction.response.send_message('Você não tem permissão para deletar esta imagem.', ephemeral=True)

    @discord.ui.button(label="Gerar Mais", style=discord.ButtonStyle.success, emoji="✨")
    async def generate_another(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.cache_key in image_cache:
            params = image_cache[self.cache_key]
            await interaction.response.defer()  # Aguarda a resposta inicial
            await generate_image(self.interaction, **params)
        else:
            await interaction.response.send_message('Não há dados de imagem para gerar outra.', ephemeral=True)

async def generate_image(interaction: discord.Interaction, **params):
    if not interaction.response.is_done():
        await interaction.response.send_message('Gerando imagem, por favor aguarde...')
    else:
        await interaction.followup.send('Gerando imagem, por favor aguarde...')

    # Verifica se o filtro está ativo e se a mensagem não é de uma DM ou chat NSFW
    global filter_active
    if filter_active and not isinstance(interaction.channel, discord.DMChannel):
        if not interaction.channel.is_nsfw() and any(word in params['prompt'].lower() for word in filter_words):
            await interaction.followup.send('O prompt contém conteúdo potencialmente NSFW e o filtro está ativado. O comando não será processado.')
            return

    width, height = map(int, params['resolution'].split('x'))

    url = "https://api.prodia.com/v1/sdxl/generate"
    payload = {
        "model": params['model'],
        "prompt": params['prompt'],
        "negative_prompt": params['negative_prompt'],
        "steps": params['steps'],
        "cfg_scale": params['cfg_scale'],
        "seed": params['seed'],
        "sampler": params['sampler'],
        "width": width,
        "height": height
    }

    if params.get('style_preset'):
        payload["style_preset"] = params['style_preset']

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        job_data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.followup.send('Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'job' not in job_data:
        await interaction.followup.send('Erro ao gerar imagem. Tente novamente mais tarde.')
        return

    job_id = job_data['job']

    image_url = None
    for _ in range(30):
        await asyncio.sleep(10)

        status_url = f"https://api.prodia.com/v1/job/{job_id}"
        status_response = requests.get(status_url, headers={"accept": "application/json", "X-Prodia-Key": API_KEY})
        try:
            status_data = status_response.json()
        except requests.exceptions.JSONDecodeError:
            await interaction.followup.send('Erro ao processar resposta da API. Tente novamente mais tarde.')
            return

        if status_data.get('status') == 'succeeded':
            image_url = status_data.get('imageUrl')
            break

    if image_url:
        embed = discord.Embed(title="Txt2Img SDXL")
        embed.add_field(name="Model", value=params['model'], inline=False)
        embed.add_field(name="Style Preset", value=params.get('style_preset') or "N/A", inline=False)
        embed.add_field(name="Steps", value=str(params['steps']), inline=False)
        embed.add_field(name="CFG Scale", value=str(params['cfg_scale']), inline=False)
        embed.add_field(name="Sampler", value=params['sampler'], inline=False)
        embed.add_field(name="Resolution", value=params['resolution'], inline=False)
        embed.set_image(url=image_url)
        embed.set_footer(text="Miuki.AI - Developed by HiroTheWolf")

        cache_key = f"{interaction.user.id}-{params['resolution']}-{params['model']}-{params['prompt']}"
        image_cache[cache_key] = params

        if not interaction.response.is_done():
            await interaction.response.edit_message(embed=embed, view=ButtonView(interaction, cache_key))
        else:
            await interaction.followup.send(embed=embed, view=ButtonView(interaction, cache_key))
    else:
        await interaction.followup.send('Erro ao gerar imagem. Tente novamente mais tarde.')

class SDXLGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_filter_words()

    def load_filter_words(self):
        global filter_words
        try:
            with open("filternsfw.txt", "r") as file:
                filter_words = [word.strip().lower() for word in file.read().split(',')]
        except FileNotFoundError:
            filter_words = []
            print("Arquivo 'filternsfw.txt' não encontrado. Nenhuma palavra de filtro carregada.")

    @app_commands.command(name="sdxlgen", description="Gera uma imagem com Stable Diffusion XL")
    @app_commands.describe(
        model="Modelo SDXL a ser usado (ex: sd_xl_base_1.0.safetensors [be9edd61])",
        prompt="Prompt para a imagem, 'masterpiece, best quality'",
        negative_prompt="O que você não quer na imagem, 'bad quality, FastNegativeV2, easynegative' (opcional)",
        style_preset="Preset de estilo (opcional)",
        steps="Número de passos, padrão: 30 (opcional)",
        cfg_scale="Escala CFG, padrão: 7 (opcional)",
        seed="Semente, padrão: -1 (opcional)",
        sampler="Sampler, padrão: DPM++ 2M Karras (opcional)",
        resolution="Resolução da imagem (largura x altura) e proporção, ex: '1024x1024 (1:1)', '1536x640 (2.4:1)'"
    )
    @app_commands.choices(
        style_preset=[app_commands.Choice(name=style, value=style) for style in style_preset_choices],
        steps=[app_commands.Choice(name=str(step), value=step) for step in [10, 20, 25, 30, 35, 40, 45, 50]],
        cfg_scale=[app_commands.Choice(name=str(scale), value=scale) for scale in [2, 5, 7, 10, 12, 15, 17, 20]],
        sampler=[app_commands.Choice(name=sampler, value=sampler) for sampler in sampler_choices],
        resolution=[
            app_commands.Choice(name='1024x1024 (1:1)', value='1024x1024'),
            app_commands.Choice(name='1152x896 (4:3)', value='1152x896'),
            app_commands.Choice(name='1216x832 (3:2)', value='1216x832'),
            app_commands.Choice(name='1344x768 (16:9)', value='1344x768'),
            app_commands.Choice(name='1536x640 (21:9)', value='1536x640'),
            app_commands.Choice(name='640x1536 (9:21)', value='640x1536'),
            app_commands.Choice(name='768x1344 (9:16)', value='768x1344'),
            app_commands.Choice(name='832x1216 (2:3)', value='832x1216')
        ]
    )
    async def sdxlgen(self, interaction: discord.Interaction, model: str, prompt: str, negative_prompt: str = "bad quality, FastNegativeV2, easynegative", style_preset: str = None, steps: int = 30, cfg_scale: int = 7, seed: int = -1, sampler: str = "DPM++ 2M Karras", resolution: str = "1024x1024"):
        params = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "style_preset": style_preset,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler": sampler,
            "resolution": resolution
        }
        await generate_image(interaction, **params)

    @app_commands.command(name="filtronsfw_sdxl", description="Ativa ou desativa o filtro anti-NSFW Stable Diffusion XL")
    async def filter_nsfw(self, interaction: discord.Interaction, state: bool):
        global filter_active
        filter_active = state
        status = "ativado" if state else "desativado"
        await interaction.response.send_message(f"Filtro anti-NSFW foi {status}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SDXLGen(bot))

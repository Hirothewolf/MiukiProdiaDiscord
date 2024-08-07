import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
from config import API_KEY
from .choices import style_preset_choices, sampler_choices

image_cache = {}
filter_active = True  # Filtro ativo por padrão

class ButtonView(discord.ui.View):
    def __init__(self, interaction, cache_key):
        super().__init__()
        self.interaction = interaction
        self.cache_key = cache_key

    @discord.ui.button(label="Deletar", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.interaction.user or interaction.user.guild_permissions.administrator:
            await interaction.message.delete()
            image_cache.pop(self.cache_key, None)
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

    # Verifica se o filtro está ativo e o prompt contém palavras NSFW
    if filter_active and any(word in params['prompt'].lower() for word in filter_words):
        await interaction.followup.send('O prompt contém conteúdo potencialmente NSFW. O comando não será processado.')
        return

    width, height = map(int, params['resolution'].split('x'))

    url = "https://api.prodia.com/v1/sd/generate"  # URL ajustada para SD 1.x
    payload = {
        "model": params['model'],
        "prompt": params['prompt'],
        "negative_prompt": params['negative_prompt'],
        "steps": params['steps'],
        "cfg_scale": params['cfg_scale'],
        "seed": params['seed'],
        "sampler": params['sampler'],
        "width": width,
        "height": height,
        "upscale": params.get('upscale', False)  # Incluído o parâmetro "upscale"
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
        embed = discord.Embed(title="Txt2Img SD 1.x")
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

class SD1xGen(commands.Cog):
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

    @app_commands.command(name="sd_1xgen", description="Gera uma imagem com Stable Diffusion 1.x")
    @app_commands.describe(
        model="Modelo SD 1.x a ser usado (ex: v1-5-pruned-emaonly.safetensors [d7049739])",
        prompt="Prompt para a imagem, 'masterpiece, best quality'",
        negative_prompt="O que você não quer na imagem, 'bad quality, FastNegativeV2, easynegative' (opcional)",
        style_preset="Preset de estilo (opcional)",
        steps="Número de passos, padrão: 30 (opcional)",
        cfg_scale="Escala CFG, padrão: 7 (opcional)",
        seed="Semente, padrão: -1 (opcional)",
        sampler="Sampler, padrão: DPM++ 2M Karras (opcional)",
        resolution="Resolução da imagem (largura x altura), ex: '1024x1024'",
        upscale="Aumentar a resolução da imagem gerada (opcional, booleano)"
    )
    @app_commands.choices(
        style_preset=[app_commands.Choice(name=style, value=style) for style in style_preset_choices],
        steps=[app_commands.Choice(name=str(step), value=step) for step in [10, 20, 25, 30, 35, 40, 45, 50]],
        cfg_scale=[app_commands.Choice(name=str(scale), value=scale) for scale in [2, 5, 7, 10, 12, 15, 17, 20]],
        sampler=[app_commands.Choice(name=sampler, value=sampler) for sampler in sampler_choices],
        resolution=[
            app_commands.Choice(name='512x512 (1:1)', value='512x512'),
            app_commands.Choice(name='768x768 (1:1)', value='768x768'),
            app_commands.Choice(name='1024x1024 (1:1)', value='1024x1024'),
            app_commands.Choice(name='768x512 (3:2)', value='768x512'),
            app_commands.Choice(name='512x768 (2:3)', value='512x768'),
            app_commands.Choice(name='768x576 (4:3)', value='768x576'),
            app_commands.Choice(name='576x768 (3:4)', value='576x768'),
            app_commands.Choice(name='912x512 (16:9)', value='912x512'),
            app_commands.Choice(name='512x912 (9:16)', value='512x912')
        ]
    )
    async def sd_1xgen(self, interaction: discord.Interaction, model: str, prompt: str, negative_prompt: str = "bad quality, FastNegativeV2, easynegative", style_preset: str = None, steps: int = 30, cfg_scale: int = 7, seed: int = -1, sampler: str = "DPM++ 2M Karras", resolution: str = "1024x1024", upscale: bool = False):
        params = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "style_preset": style_preset,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler": sampler,
            "resolution": resolution,
            "upscale": upscale
        }
        await generate_image(interaction, **params)

    @app_commands.command(name="filtronsfw_sd1x", description="Ativa ou desativa o filtro anti-NSFW Stable Diffusion 1.x")
    async def filter_nsfw(self, interaction: discord.Interaction, state: bool):
        global filter_active
        filter_active = state
        status = "ativado" if state else "desativado"
        await interaction.response.send_message(f"Filtro anti-NSFW foi {status}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SD1xGen(bot))

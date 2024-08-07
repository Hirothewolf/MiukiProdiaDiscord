import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import base64
import io
from PIL import Image
from config import API_KEY
from .choices import upscale_models
import aiohttp

image_cache = {}

class ButtonView(discord.ui.View):
    def __init__(self, interaction, cache_key):
        super().__init__()
        self.interaction = interaction
        self.cache_key = cache_key

    @discord.ui.button(label="🗑️ Deletar", style=discord.ButtonStyle.danger)
    async def delete_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.interaction.user or interaction.user.guild_permissions.administrator:
            await interaction.message.delete()
            image_cache.pop(self.cache_key, None)
        else:
            await interaction.response.send_message('Você não tem permissão para deletar esta imagem.', ephemeral=True)

async def upscale_image(interaction: discord.Interaction, **params):
    if not interaction.response.is_done():
        await interaction.response.send_message('Realizando upscale, por favor aguarde...')
    else:
        await interaction.followup.send('Realizando upscale, por favor aguarde...')

    url = "https://api.prodia.com/v1/upscale"
    payload = {
        "resize": params['resize'],
        "model": params['model'],
    }

    if params.get('image_url'):
        payload["imageUrl"] = params['image_url']

    if params.get('image_data'):
        payload["imageData"] = params['image_data']

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": API_KEY
    }

    # Log para depuração
    print("Payload enviado para API Prodia:", payload)

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Lança um erro para respostas HTTP não 200
        job_data = response.json()
    except requests.exceptions.RequestException as e:
        await interaction.followup.send(f'Erro ao processar a solicitação: {e}')
        return
    except requests.exceptions.JSONDecodeError:
        await interaction.followup.send('Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'job' not in job_data:
        await interaction.followup.send('Erro ao realizar upscale. Tente novamente mais tarde.')
        return

    job_id = job_data['job']

    image_url = None
    for _ in range(30):
        await asyncio.sleep(10)

        status_url = f"https://api.prodia.com/v1/job/{job_id}"
        try:
            status_response = requests.get(status_url, headers={"accept": "application/json", "X-Prodia-Key": API_KEY})
            status_response.raise_for_status()
            status_data = status_response.json()
        except requests.exceptions.RequestException as e:
            await interaction.followup.send(f'Erro ao processar a solicitação: {e}')
            return
        except requests.exceptions.JSONDecodeError:
            await interaction.followup.send('Erro ao processar resposta da API. Tente novamente mais tarde.')
            return

        if status_data.get('status') == 'succeeded':
            image_url = status_data.get('imageUrl')
            break

    if image_url:
        embed = discord.Embed(title="Upscale Imagem")
        embed.add_field(name="Modelo", value=params['model'], inline=False)
        embed.add_field(name="Fator de Resize", value=f"{params['resize']}x", inline=False)
        embed.set_image(url=image_url)
        embed.set_footer(text="Miuki.AI - Desenvolvido por HiroTheWolf")

        cache_key = f"{interaction.user.id}-{params['resize']}-{params['model']}"
        image_cache[cache_key] = {
            'resize': params['resize'],
            'model': params['model'],
            'image_url': image_url,
            'image_data': params.get('image_data')
        }

        if not interaction.response.is_done():
            await interaction.response.edit_message(embed=embed, view=ButtonView(interaction, cache_key))
        else:
            await interaction.followup.send(embed=embed, view=ButtonView(interaction, cache_key))
    else:
        await interaction.followup.send('Erro ao realizar upscale. Tente novamente mais tarde.')

class Upscale(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="upscale", description="Realiza o upscale de uma imagem")
    @app_commands.describe(
        image_url="URL da imagem a ser upscaled",
        image_data="Upload de arquivo para a imagem a ser upscaled",
        resize="Fator de resize (2x ou 4x)",
        model="Modelo para upscale"
    )
    @app_commands.choices(
        resize=[app_commands.Choice(name="2x", value=2), app_commands.Choice(name="4x", value=4)],
        model=[app_commands.Choice(name=model, value=model) for model in upscale_models]
    )
    async def upscale(self, interaction: discord.Interaction,
                      image_url: str = None,
                      image_data: discord.Attachment = None,
                      resize: int = 4,
                      model: str = "ESRGAN_4x"):

        await interaction.response.send_message('Realizando upscale, por favor aguarde...')

        if image_url is None and image_data is None:
            await interaction.edit_original_response(content='Você deve fornecer um URL de imagem ou um arquivo de imagem.')
            return

        if image_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.head(image_url) as resp:
                        if resp.status != 200:
                            await interaction.edit_original_response(content='URL da imagem é inválida.')
                            return
                        content_length = int(resp.headers.get('Content-Length', 0))
                        if content_length > 5 * 1024 * 1024:  # 5 MB limit
                            await interaction.edit_original_response(content='A imagem é muito grande. O tamanho máximo permitido é 5 MB.')
                            return
            except Exception:
                await interaction.edit_original_response(content='Erro ao verificar a imagem na URL fornecida.')
                return
            image_base64 = None

        if image_data:
            image_bytes = await image_data.read()
            try:
                image = Image.open(io.BytesIO(image_bytes))
                if image.size[0] * image.size[1] > 5000 * 5000:  # 25,000,000 pixels limit
                    await interaction.edit_original_response(content='A imagem é muito grande. O tamanho máximo permitido é 25 milhões de pixels.')
                    return
                with io.BytesIO() as output:
                    if image.format not in ["JPEG", "PNG"]:
                        image = image.convert("RGB")
                    image.save(output, format="PNG")
                    image_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
            except Exception:
                await interaction.edit_original_response(content='Erro ao processar a imagem fornecida. Certifique-se de que é um arquivo de imagem válido.')
                return

        url = "https://api.prodia.com/v1/upscale"
        payload = {
            "resize": resize,
            "model": model,
        }

        if image_url:
            payload["imageUrl"] = image_url

        if image_base64:
            payload["imageData"] = image_base64

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": API_KEY
        }

        # Log para depuração
        print("Payload enviado para API Prodia:", payload)

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            job_data = response.json()
        except requests.exceptions.RequestException as e:
            await interaction.edit_original_response(content=f'Erro ao processar a solicitação: {e}')
            return
        except requests.exceptions.JSONDecodeError:
            await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
            return

        if 'job' not in job_data:
            await interaction.edit_original_response(content='Erro ao realizar upscale. Tente novamente mais tarde.')
            return

        job_id = job_data['job']

        image_url = None
        for _ in range(30):
            await asyncio.sleep(10)

            status_url = f"https://api.prodia.com/v1/job/{job_id}"
            try:
                status_response = requests.get(status_url, headers={"accept": "application/json", "X-Prodia-Key": API_KEY})
                status_response.raise_for_status()
                status_data = status_response.json()
            except requests.exceptions.RequestException as e:
                await interaction.edit_original_response(content=f'Erro ao processar a solicitação: {e}')
                return
            except requests.exceptions.JSONDecodeError:
                await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
                return

            if status_data.get('status') == 'succeeded':
                image_url = status_data.get('imageUrl')
                break

        if image_url:
            embed = discord.Embed(title="Upscale Image")
            embed.add_field(name="Modelo", value=model, inline=False)
            embed.add_field(name="Fator de Resize", value=f"{resize}x", inline=False)
            embed.set_image(url=image_url)
            embed.set_footer(text="Miuki.AI - Desenvolvido por HiroTheWolf")

            cache_key = f"{interaction.user.id}-{resize}-{model}"
            image_cache[cache_key] = {
                'resize': resize,
                'model': model,
                'image_url': image_url,
                'image_data': image_base64
            }

            if not interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=ButtonView(interaction, cache_key))
            else:
                await interaction.followup.send(embed=embed, view=ButtonView(interaction, cache_key))
        else:
            await interaction.edit_original_response(content='Erro ao realizar upscale. Tente novamente mais tarde.')

async def setup(bot):
    await bot.add_cog(Upscale(bot))

import discord
from discord import app_commands
from discord.ext import commands
import requests
import asyncio
import base64
import aiohttp
from PIL import Image
import io
import base64

TOKEN = 'Token do seu Bot Discord'
PRODIA_API_KEY = 'Sua API-KEY'

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

model_choices = []
loras_sdxl = []
loras_sd1x = []
style_preset_choices = [
    "3d-model", "analog-film", "anime", "cinematic", "comic-book", "digital-art",
    "enhance", "fantasy-art", "isometric", "line-art", "low-poly", "neon-punk",
    "origami", "photographic", "pixel-art", "texture", "craft-clay"
]
sampler_choices = [
    "DPM++ 2M Karras", "DPM++ SDE Karras", "DPM++ 2M SDE Exponential", "DPM++ 2M SDE Karras", "Euler a", "Euler", "LMS", "Heun", "DPM2", "DPM2 a", "DPM++ 2S a", "DPM++ 2M", "DPM++ SDE", "DPM++ 2M SDE", "DPM++ 2M SDE Heun", "DPM++ 2M SDE Heun Karras", "DPM++ 2M SDE Heun Exponential", "DPM++ 3M SDE", "DPM++ 3M SDE Karras", "DPM fast"
]
upscale_models = [
    "ESRGAN_4x", "Lanczos", "Nearest", "LDSR", "R-ESRGAN 4x+", 
    "R-ESRGAN 4x+ Anime6B", "ScuNET GAN", "ScuNET PSNR", "SwinIR 4x"
]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Inicializando as variáveis globais para os modelos e Loras
model_choices_sdxl = []
model_choices_sd1 = []
loras_sdxl = []
loras_sd1x = []

@bot.event
async def on_ready():
    await bot.user.edit(username='Miuki')
    await fetch_model_choices_sdxl()
    await fetch_model_choices_sd1()
    await fetch_loras_sdxl()
    await fetch_loras_sd1x()
    await bot.tree.sync()
    print(f'We have logged in as {bot.user}')

async def fetch_model_choices_sdxl():
    url = "https://api.prodia.com/v1/sdxl/models"
    headers = {
        "accept": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        global model_choices_sdxl
        model_choices_sdxl = response.json()
        print(f"SDXL Models fetched: {model_choices_sdxl}")  # Debug
    else:
        print(f"Failed to fetch SDXL model choices. Status code: {response.status_code}")

async def fetch_model_choices_sd1():
    url = "https://api.prodia.com/v1/sd/models"
    headers = {
        "accept": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        global model_choices_sd1
        model_choices_sd1 = response.json()
        print(f"SD1 Models fetched: {model_choices_sd1}")  # Debug
    else:
        print(f"Failed to fetch SD1 model choices. Status code: {response.status_code}")

async def fetch_loras_sdxl():
    url = "https://api.prodia.com/v1/sdxl/loras"
    headers = {
        "accept": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        global loras_sdxl
        loras_sdxl = response.json()
        print(f"Loras SDXL fetched: {loras_sdxl}")  # Debug
    else:
        print(f"Failed to fetch SDXL Loras. Status code: {response.status_code}")

async def fetch_loras_sd1x():
    url = "https://api.prodia.com/v1/sd/loras"
    headers = {
        "accept": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        global loras_sd1x
        loras_sd1x = response.json()
        print(f"Loras SD 1.X fetched: {loras_sd1x}")  # Debug
    else:
        print(f"Failed to fetch SD1x Loras. Status code: {response.status_code}")

def split_into_chunks(strings, chunk_size):
    """Divide uma lista de strings em blocos de tamanho fixo."""
    return [strings[i:i + chunk_size] for i in range(0, len(strings), chunk_size)]

def format_list(title, items):
    """Formata a lista de itens com um título."""
    return f"{title}\n" + "\n".join(items)

@bot.tree.command(name="models_sdxl", description="Lista todos os modelos SDXL disponíveis")
async def models_sdxl(interaction: discord.Interaction):
    if not model_choices_sdxl:
        await interaction.response.send_message("Nenhum modelo SDXL disponível no momento. Tente novamente mais tarde.")
        return

    sdxl_chunks = split_into_chunks(model_choices_sdxl, 20)
    for i, chunk in enumerate(sdxl_chunks):
        header = "**Modelos SDXL disponíveis:**\n" if i == 0 else ""
        message = format_list(header, chunk)
        if i == 0:
            await interaction.response.send_message(message)
        else:
            await interaction.followup.send(message)

@bot.tree.command(name="models_sd1x", description="Lista todos os modelos SD 1.X disponíveis")
async def models_sd1x(interaction: discord.Interaction):
    if not model_choices_sd1:
        await interaction.response.send_message("Nenhum modelo SD 1.X disponível no momento. Tente novamente mais tarde.")
        return

    sd1_chunks = split_into_chunks(model_choices_sd1, 20)
    for i, chunk in enumerate(sd1_chunks):
        header = "**Modelos SD 1.X disponíveis:**\n" if i == 0 else ""
        message = format_list(header, chunk)
        if i == 0:
            await interaction.response.send_message(message)
        else:
            await interaction.followup.send(message)

@bot.tree.command(name="lora_sdxl", description="Lista todos os Loras SDXL disponíveis")
async def lora_sdxl(interaction: discord.Interaction):
    if not loras_sdxl:
        await interaction.response.send_message("Nenhum Lora SDXL disponível no momento. Tente novamente mais tarde.")
        return

    description = "Uso geral dentro de um prompt: `<lora:LoraName:weight>`"
    sdxl_chunks = split_into_chunks(loras_sdxl, 15)
    for i, chunk in enumerate(sdxl_chunks):
        header = f"**Loras SDXL disponíveis:**\n{description}\n" if i == 0 else ""
        message = format_list(header, chunk)
        if i == 0:
            await interaction.response.send_message(message)
        else:
            await interaction.followup.send(message)

@bot.tree.command(name="lora_sd1x", description="Lista todos os Loras SD 1.X disponíveis")
async def lora_sd1x(interaction: discord.Interaction):
    if not loras_sd1x:
        await interaction.response.send_message("Nenhum Lora SD 1.X disponível no momento. Tente novamente mais tarde.")
        return

    description = "Uso geral dentro de um prompt: `<lora:LoraName:weight>`"
    sd1_chunks = split_into_chunks(loras_sd1x, 15)
    for i, chunk in enumerate(sd1_chunks):
        header = f"**Loras SD 1.X disponíveis:**\n{description}\n" if i == 0 else ""
        message = format_list(header, chunk)
        if i == 0:
            await interaction.response.send_message(message)
        else:
            await interaction.followup.send(message)

#####################################
#### /sdxlgen Command
#####################################

@bot.tree.command(name="sdxlgen", description="Gera uma imagem com Stable Diffusion XL")
@app_commands.describe(
    model="Modelo SDXL a ser usado (ex: sd_xl_base_1.0.safetensors [be9edd61])",
    prompt="Prompt para a imagem, 'masterpiece, best quality'",
    negative_prompt="O que voce não quer na imagem, 'bad quality, FastNegativeV2, easynegative')",
    style_preset="Preset de estilo (opcional)",
    steps="Número de passos, padrão: 30 (opcional)",
    cfg_scale="Escala CFG, padrão: 7 (opcional)",
    seed="Semente, padrão: -1 (opcional)",
    sampler="Sampler, padrão: DPM++ 2M Karras (opcional)",
    width="Largura da imagem, padrão: 1024",
    height="Altura da imagem, padrão: 1024"
)
@app_commands.choices(
    style_preset=[app_commands.Choice(name=style, value=style) for style in style_preset_choices],
    steps=[app_commands.Choice(name=str(step), value=step) for step in [10, 20, 25, 30, 35, 40, 45, 50]],
    cfg_scale=[app_commands.Choice(name=str(scale), value=scale) for scale in [2, 5, 7, 10, 12, 15, 17, 20]],
    sampler=[app_commands.Choice(name=sampler, value=sampler) for sampler in sampler_choices],
    width=[app_commands.Choice(name=str(w), value=w) for w in [128, 256, 512, 768, 1024]],
    height=[app_commands.Choice(name=str(h), value=h) for h in [128, 256, 512, 768, 1024]]
)
async def sdxlgen(interaction: discord.Interaction,
                   model: str,
                   prompt: str,
                   negative_prompt: str,
                   style_preset: str = None,
                   steps: int = 30,
                   cfg_scale: int = 7,
                   seed: int = -1,
                   sampler: str = "DPM++ 2M Karras",
                   width: int = 1024,
                   height: int = 1024):

    await interaction.response.send_message('Gerando imagem, por favor aguarde...')

    url = "https://api.prodia.com/v1/sdxl/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
        "sampler": sampler,
        "width": width,
        "height": height
    }

    if style_preset:
        payload["style_preset"] = style_preset

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        job_data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'job' not in job_data:
        await interaction.edit_original_response(content='Erro ao gerar imagem. Tente novamente mais tarde.')
        return

    job_id = job_data['job']

    image_url = None
    for _ in range(30):
        await asyncio.sleep(10)

        status_url = f"https://api.prodia.com/v1/job/{job_id}"
        status_response = requests.get(status_url, headers={"accept": "application/json", "X-Prodia-Key": PRODIA_API_KEY})
        try:
            status_data = status_response.json()
        except requests.exceptions.JSONDecodeError:
            await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
            return

        if status_data.get('status') == 'succeeded':
            image_url = status_data.get('imageUrl')
            break

    if image_url:
        await interaction.edit_original_response(content=f'Imagem gerada: {image_url}')
    else:
        await interaction.edit_original_response(content='Erro ao gerar imagem. Tente novamente mais tarde.')

#####################################
#### /sdxl_inpaint Command(WIP)
#####################################

#@bot.tree.command(name="sdxl_inpaint", description="Realiza inpainting em uma imagem com Stable Diffusion XL")
@app_commands.describe(
    image_url="URL da imagem a ser inpainted (opcional)",
    image_data="Upload de arquivo para a imagem a ser inpainted (Arquivo/base64)",
    mask_url="URL da máscara (opcional)",
    mask_data="Upload de arquivo para a máscara (Arquivo/base64)",
    model="Modelo SDXL a ser usado (ex: sd_xl_base_1.0.safetensors [be9edd61])",
    prompt="Prompt para a imagem, 'masterpiece, best quality'",
    denoising_strength="Força de denoising",
    negative_prompt="O que voce não quer na imagem, 'bad quality, FastNegativeV2, easynegative')",
    style_preset="Preset de estilo (opcional)",
    steps="Número de passos, padrão: 30 (opcional)",
    cfg_scale="Escala CFG, padrão: 7 (opcional)",
    seed="Semente, padrão: -1 (opcional)",
    upscale="Upscale",
    mask_blur="Blur da máscara",
    inpainting_fill="Preenchimento do inpainting",
    inpainting_mask_invert="Inversão da máscara",
    sampler="Sampler, padrão: DPM++ 2M Karras (opcional)",
    width="Largura da imagem, padrão: 1024",
    height="Altura da imagem, padrão: 1024"
)
@app_commands.choices(
    style_preset=[app_commands.Choice(name=style, value=style) for style in style_preset_choices],
    steps=[app_commands.Choice(name=str(step), value=step) for step in [10, 20, 25, 30, 35, 40, 45, 50]],
    cfg_scale=[app_commands.Choice(name=str(scale), value=scale) for scale in [2, 5, 7, 10, 12, 15, 17, 20]],
    sampler=[app_commands.Choice(name=sampler, value=sampler) for sampler in sampler_choices],
    width=[app_commands.Choice(name=str(w), value=w) for w in [128, 256, 512, 768, 1024]],
    height=[app_commands.Choice(name=str(h), value=h) for h in [128, 256, 512, 768, 1024]]
)
async def sdxl_inpaint(interaction: discord.Interaction,
                       model: str,
                       prompt: str,
                       denoising_strength: float,
                       negative_prompt: str,
                       upscale: bool,
                       mask_blur: int,
                       inpainting_fill: int,
                       inpainting_mask_invert: int,
                       image_url: str = None,
                       image_data: discord.Attachment = None,
                       mask_url: str = None,
                       mask_data: discord.Attachment = None,
                       style_preset: str = None,
                       steps: int = 30,
                       cfg_scale: int = 7,
                       seed: int = -1,
                       sampler: str = "DPM++ 2M Karras",
                       width: int = 1024,
                       height: int = 1024):

    await interaction.response.send_message('Realizando inpainting, por favor aguarde...')

    if (image_url is None and image_data is None) or (mask_url is None and mask_data is None):
        await interaction.edit_original_response(content='Você deve fornecer um URL de imagem e um URL de máscara ou arquivos de imagem e máscara.')
        return

    if image_data:
        image_bytes = await image_data.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    else:
        image_base64 = None

    if mask_data:
        mask_bytes = await mask_data.read()
        mask_base64 = base64.b64encode(mask_bytes).decode('utf-8')
    else:
        mask_base64 = None

    url = "https://api.prodia.com/v1/sdxl/inpainting"
    payload = {
        "model": model,
        "prompt": prompt,
        "denoising_strength": denoising_strength,
        "negative_prompt": negative_prompt,
        "upscale": upscale,
        "mask_blur": mask_blur,
        "inpainting_fill": inpainting_fill,
        "inpainting_mask_invert": inpainting_mask_invert,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
        "sampler": sampler,
        "width": width,
        "height": height
    }

    if image_url:
        payload["imageUrl"] = image_url

    if image_base64:
        payload["imageData"] = image_base64

    if mask_url:
        payload["maskUrl"] = mask_url

    if mask_base64:
        payload["maskData"] = mask_base64

    if style_preset:
        payload["style_preset"] = style_preset

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        job_data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'job' not in job_data:
        await interaction.edit_original_response(content='Erro ao realizar inpainting. Tente novamente mais tarde.')
        return

    job_id = job_data['job']

    image_url = None
    for _ in range(30):
        await asyncio.sleep(10)

        status_url = f"https://api.prodia.com/v1/job/{job_id}"
        status_response = requests.get(status_url, headers={"accept": "application/json", "X-Prodia-Key": PRODIA_API_KEY})
        try:
            status_data = status_response.json()
        except requests.exceptions.JSONDecodeError:
            await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
            return

        if status_data.get('status') == 'succeeded':
            image_url = status_data.get('imageUrl')
            break

    if image_url:
        await interaction.edit_original_response(content=f'Imagem inpainted: {image_url}')
    else:
        await interaction.edit_original_response(content='Erro ao realizar inpainting. Tente novamente mais tarde.')

    
#####################################
#### /upscale Command
#####################################

@bot.tree.command(name="upscale", description="Realiza o upscale de uma imagem")
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
async def upscale(interaction: discord.Interaction,
                   image_url: str = None,
                   image_data: discord.Attachment = None,
                   resize: int = 4,
                   model: str = "ESRGAN_4x"):

    await interaction.response.send_message('Realizando upscale, por favor aguarde...')

    if image_url is None and image_data is None:
        await interaction.edit_original_response(content='Você deve fornecer um URL de imagem ou um arquivo de imagem.')
        return

    if image_data:
        # Ler os dados da imagem e converter para PNG se necessário
        image_bytes = await image_data.read()
        try:
            image = Image.open(io.BytesIO(image_bytes))
            with io.BytesIO() as output:
                if image.format not in ["JPEG", "PNG"]:
                    image = image.convert("RGB")  # Converter para RGB se necessário
                image.save(output, format="PNG")  # Salvar como PNG para compatibilidade
                image_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
        except Exception as e:
            await interaction.edit_original_response(content='Erro ao processar a imagem fornecida. Certifique-se de que é um arquivo de imagem válido.')
            return
    else:
        image_base64 = None

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
        "X-Prodia-Key": PRODIA_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        job_data = response.json()
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
        status_response = requests.get(status_url, headers={"accept": "application/json", "X-Prodia-Key": PRODIA_API_KEY})
        try:
            status_data = status_response.json()
        except requests.exceptions.JSONDecodeError:
            await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
            return

        if status_data.get('status') == 'succeeded':
            image_url = status_data.get('imageUrl')
            break

    if image_url:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    file = discord.File(fp=io.BytesIO(image_data), filename="upscaled_image.png")
                    await interaction.followup.send(content='Imagem upscaled:', file=file)
                else:
                    await interaction.edit_original_response(content='Erro ao baixar a imagem upscaled. Tente novamente mais tarde.')
    else:
        await interaction.edit_original_response(content='Erro ao realizar upscale. Tente novamente mais tarde.')

#####################################
#### /sd_1xgen Command
#####################################

@bot.tree.command(name="sd_1xgen", description="Gera uma imagem com o Stable Diffusion 1.x")
@app_commands.describe(
    model="Modelo SD 1.x a ser usado (deixe em branco para usar o padrão 'v1-5-pruned-emaonly.safetensors [d7049739]')",
    prompt="Prompt para a imagem, 'masterpiece, best quality'",
    negative_prompt="O que voce não quer na imagem, 'bad quality, FastNegativeV2, easynegative",
    style_preset="Preset de estilo (opcional)",
    steps="Número de passos, padrão: 30 (opcional)",
    cfg_scale="Escala CFG, padrão: 7 (opcional)",
    seed="Semente, padrão: -1 (opcional)",
    sampler="Sampler, padrão: DPM++ 2M Karras (opcional)",
    width="Largura da imagem, padrão: 1024",
    height="Altura da imagem, padrão: 1024",
    upscale="Aumentar a resolução da imagem (True/False)"
)
@app_commands.choices(
    style_preset=[app_commands.Choice(name=style, value=style) for style in style_preset_choices],
    steps=[app_commands.Choice(name=str(step), value=step) for step in [10, 20, 25, 30, 35, 40, 45, 50]],
    cfg_scale=[app_commands.Choice(name=str(scale), value=scale) for scale in [2, 5, 7, 10, 12, 15, 17, 20]],
    sampler=[app_commands.Choice(name=sampler, value=sampler) for sampler in sampler_choices],
    width=[app_commands.Choice(name=str(w), value=w) for w in [128, 256, 512, 768, 1024]],
    height=[app_commands.Choice(name=str(h), value=h) for h in [128, 256, 512, 768, 1024]]
)
async def sd_1x(interaction: discord.Interaction,
                prompt: str,
                model: str = "v1-5-pruned-emaonly.safetensors [d7049739]",
                negative_prompt: str = "bad quality, FastNegativeV2, easynegative",
                style_preset: str = None,
                steps: int = 20,
                cfg_scale: int = 7,
                seed: int = -1,
                sampler: str = "DPM++ 2M Karras",
                width: int = 512,
                height: int = 512,
                upscale: bool = False):

    await interaction.response.send_message('Gerando imagem, por favor aguarde...')

    url = "https://api.prodia.com/v1/sd/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "seed": seed,
        "sampler": sampler,
        "width": width,
        "height": height,
        "upscale": upscale
    }

    if style_preset:
        payload["style_preset"] = style_preset

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        job_data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'job' not in job_data:
        await interaction.edit_original_response(content='Erro ao gerar imagem. Tente novamente mais tarde.')
        return

    job_id = job_data['job']

    image_url = None
    for _ in range(30):
        await asyncio.sleep(10)

        status_url = f"https://api.prodia.com/v1/job/{job_id}"
        status_response = requests.get(status_url, headers={"accept": "application/json", "X-Prodia-Key": PRODIA_API_KEY})
        try:
            status_data = status_response.json()
        except requests.exceptions.JSONDecodeError:
            await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
            return

        if status_data.get('status') == 'succeeded':
            image_url = status_data.get('imageUrl')
            break

    if image_url:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    file = discord.File(fp=io.BytesIO(image_data), filename="generated_image.png")
                    await interaction.followup.send(content='Imagem gerada:', file=file)
                else:
                    await interaction.edit_original_response(content='Erro ao baixar a imagem gerada. Tente novamente mais tarde.')
    else:
        await interaction.edit_original_response(content='Erro ao gerar imagem. Tente novamente mais tarde.')

#####################################
#### /sd1x_controlnet Command
#####################################


#####################################
#### /facerestorer Command
#####################################

@bot.tree.command(name="facerestorer", description="Restaura o rosto em uma imagem")
@app_commands.describe(
    image_url="URL da imagem para restauração (opcional)",
    image_data="Upload de arquivo para imagem a ser restaurada (base64)"
)
async def facerestorer(interaction: discord.Interaction,
                       image_url: str = None,
                       image_data: discord.Attachment = None):

    await interaction.response.send_message('Restaurando imagem, por favor aguarde...')

    if image_url is None and image_data is None:
        await interaction.edit_original_response(content='Você deve fornecer um URL de imagem ou um arquivo de imagem.')
        return

    if image_data:
        image_bytes = await image_data.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    else:
        image_base64 = None

    url = "https://api.prodia.com/v1/facerestore"
    payload = {}
    
    if image_url:
        payload["imageUrl"] = image_url

    if image_base64:
        payload["imageData"] = image_base64

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        result_data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'imageUrl' not in result_data:
        await interaction.edit_original_response(content='Erro ao restaurar imagem. Tente novamente mais tarde.')
        return

    restored_image_url = result_data['imageUrl']

    async with aiohttp.ClientSession() as session:
        async with session.get(restored_image_url) as resp:
            if resp.status == 200:
                image_data = await resp.read()
                file = discord.File(fp=io.BytesIO(image_data), filename="restored_image.png")
                await interaction.followup.send(content='Imagem restaurada:', file=file)
            else:
                await interaction.edit_original_response(content='Erro ao baixar a imagem restaurada. Tente novamente mais tarde.')


#####################################
#### /faceswap Command
#####################################

@bot.tree.command(name="faceswap", description="Troca de rostos entre duas imagens")
@app_commands.describe(
    source_url="URL da imagem fonte (opcional)",
    target_url="URL da imagem alvo (opcional)",
    source_data="Upload de arquivo para a imagem fonte (base64)",
    target_data="Upload de arquivo para a imagem alvo (base64)"
)
async def faceswap(interaction: discord.Interaction,
                   source_url: str = None,
                   target_url: str = None,
                   source_data: discord.Attachment = None,
                   target_data: discord.Attachment = None):

    await interaction.response.send_message('Processando a troca de rostos, por favor aguarde...')

    if (source_url is None and source_data is None) or (target_url is None and target_data is None):
        await interaction.edit_original_response(content='Você deve fornecer um URL de imagem ou um arquivo de imagem para ambas as fontes e alvos.')
        return

    payload = {}

    if source_url:
        payload["sourceUrl"] = source_url
    elif source_data:
        source_bytes = await source_data.read()
        payload["sourceData"] = base64.b64encode(source_bytes).decode('utf-8')

    if target_url:
        payload["targetUrl"] = target_url
    elif target_data:
        target_bytes = await target_data.read()
        payload["targetData"] = base64.b64encode(target_bytes).decode('utf-8')

    url = "https://api.prodia.com/v1/faceswap"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        result_data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'imageUrl' not in result_data:
        await interaction.edit_original_response(content='Erro ao realizar troca de rostos. Tente novamente mais tarde.')
        return

    swapped_image_url = result_data['imageUrl']

    async with aiohttp.ClientSession() as session:
        async with session.get(swapped_image_url) as resp:
            if resp.status == 200:
                image_data = await resp.read()
                file = discord.File(fp=io.BytesIO(image_data), filename="swapped_faces.png")
                await interaction.followup.send(content='Imagem com rostos trocados:', file=file)
            else:
                await interaction.edit_original_response(content='Erro ao baixar a imagem com rostos trocados. Tente novamente mais tarde.')


#####################################
#### /photomaker Command
#####################################

@bot.tree.command(name="photomaker", description="Gera imagens com consistência de personagem")
@app_commands.describe(
    image_urls="URLs das imagens (opcional, múltiplos URLs separados por vírgula)",
    image_data="Uploads de arquivos de imagem (opcional, múltiplos arquivos)",
    prompt="Prompt para a imagem",
    negative_prompt="Prompt negativo",
    style_preset="Preset de estilo (opcional)",
    strength="Força (0-100)",
    steps="Número de passos",
    seed="Semente",
    cfg_scale="Escala CFG"
)
@app_commands.choices(
    style_preset=[app_commands.Choice(name=style, value=style) for style in style_preset_choices],
    steps=[app_commands.Choice(name=str(step), value=step) for step in [10, 20, 25, 30, 35, 40, 45, 50]],
    cfg_scale=[app_commands.Choice(name=str(scale), value=scale) for scale in [2, 5, 7, 10, 12, 15, 17, 20]]
)
async def photomaker(interaction: discord.Interaction,
                     image_urls: str = None,
                     image_data: discord.Attachment = None,
                     prompt: str = "man img wearing a hat",
                     negative_prompt: str = "badly drawn",
                     style_preset: str = "anime",
                     strength: int = 20,
                     steps: int = 20,
                     seed: int = 0,
                     cfg_scale: int = 0):

    await interaction.response.send_message('Gerando imagem com consistência de personagem, por favor aguarde...')

    image_urls_list = image_urls.split(",") if image_urls else []
    image_data_list = []

    if image_data:
        for attachment in image_data:
            image_bytes = await attachment.read()
            image_data_list.append(base64.b64encode(image_bytes).decode('utf-8'))

    payload = {
        "imageUrls": image_urls_list,
        "imageData": image_data_list,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "style_preset": style_preset,
        "strength": strength,
        "steps": steps,
        "seed": seed,
        "cfg_scale": cfg_scale
    }

    url = "https://api.prodia.com/v1/photomaker"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Prodia-Key": PRODIA_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        result_data = response.json()
    except requests.exceptions.JSONDecodeError:
        await interaction.edit_original_response(content='Erro ao processar resposta da API. Tente novamente mais tarde.')
        return

    if 'imageUrl' not in result_data:
        await interaction.edit_original_response(content='Erro ao gerar imagem. Tente novamente mais tarde.')
        return

    generated_image_url = result_data['imageUrl']

    async with aiohttp.ClientSession() as session:
        async with session.get(generated_image_url) as resp:
            if resp.status == 200:
                image_data = await resp.read()
                file = discord.File(fp=io.BytesIO(image_data), filename="photomaker_image.png")
                await interaction.followup.send(content='Aqui está a imagem gerada com consistência de personagem:', file=file)
            else:
                await interaction.edit_original_response(content='Erro ao baixar a imagem gerada. Tente novamente mais tarde.')

#####################################
#####################################


bot.run(TOKEN)

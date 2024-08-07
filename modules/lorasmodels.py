import discord
from discord.ext import commands
import requests
from config import API_KEY

class LorasModels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_choices_sdxl = []
        self.model_choices_sd1 = []
        self.loras_sdxl = []
        self.loras_sd1x = []
        self.fetch_data_task = bot.loop.create_task(self.fetch_data())  # Adiciona a tarefa para buscar dados

    async def fetch_data(self):
        await self.fetch_model_choices_sdxl()
        await self.fetch_model_choices_sd1()
        await self.fetch_loras_sdxl()
        await self.fetch_loras_sd1x()

    async def fetch_model_choices_sdxl(self):
        url = "https://api.prodia.com/v1/sdxl/models"
        headers = {
            "accept": "application/json",
            "X-Prodia-Key": API_KEY
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.model_choices_sdxl = response.json()
            print(f"SDXL Models fetched: {self.model_choices_sdxl}")  # Debug
        else:
            print(f"Failed to fetch SDXL model choices. Status code: {response.status_code}")

    async def fetch_model_choices_sd1(self):
        url = "https://api.prodia.com/v1/sd/models"
        headers = {
            "accept": "application/json",
            "X-Prodia-Key": API_KEY
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.model_choices_sd1 = response.json()
            print(f"SD1 Models fetched: {self.model_choices_sd1}")  # Debug
        else:
            print(f"Failed to fetch SD1 model choices. Status code: {response.status_code}")

    async def fetch_loras_sdxl(self):
        url = "https://api.prodia.com/v1/sdxl/loras"
        headers = {
            "accept": "application/json",
            "X-Prodia-Key": API_KEY
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.loras_sdxl = response.json()
            print(f"Loras SDXL fetched: {self.loras_sdxl}")  # Debug
        else:
            print(f"Failed to fetch SDXL Loras. Status code: {response.status_code}")

    async def fetch_loras_sd1x(self):
        url = "https://api.prodia.com/v1/sd/loras"
        headers = {
            "accept": "application/json",
            "X-Prodia-Key": API_KEY
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.loras_sd1x = response.json()
            print(f"Loras SD 1.X fetched: {self.loras_sd1x}")  # Debug
        else:
            print(f"Failed to fetch SD1x Loras. Status code: {response.status_code}")

    @discord.app_commands.command(name="models_sdxl", description="Lista todos os modelos SDXL disponíveis")
    async def models_sdxl(self, interaction: discord.Interaction):
        if not self.model_choices_sdxl:
            await interaction.response.send_message("Nenhum modelo SDXL disponível no momento. Tente novamente mais tarde.")
            return

        response_message = "**Modelos SDXL disponíveis:**\n"
        chunks = list(self.split_list(self.model_choices_sdxl, 40))

        await interaction.response.send_message(f"{response_message}```\n{self.format_list(chunks[0])}\n```")

        for chunk in chunks[1:]:
            await interaction.followup.send(f"```\n{self.format_list(chunk)}\n```")

    @discord.app_commands.command(name="models_sd1x", description="Lista todos os modelos SD 1.X disponíveis")
    async def models_sd1x(self, interaction: discord.Interaction):
        if not self.model_choices_sd1:
            await interaction.response.send_message("Nenhum modelo SD 1.X disponível no momento. Tente novamente mais tarde.")
            return

        response_message = "**Modelos SD 1.X disponíveis:**\n"
        chunks = list(self.split_list(self.model_choices_sd1, 40))

        await interaction.response.send_message(f"{response_message}```\n{self.format_list(chunks[0])}\n```")

        for chunk in chunks[1:]:
            await interaction.followup.send(f"```\n{self.format_list(chunk)}\n```")

    @discord.app_commands.command(name="lora_sdxl", description="Lista todos os Loras SDXL disponíveis")
    async def lora_sdxl(self, interaction: discord.Interaction):
        if not self.loras_sdxl:
            await interaction.response.send_message("Nenhum Lora SDXL disponível no momento. Tente novamente mais tarde.")
            return

        description = "Uso geral dentro de um prompt: `<lora:LoraName:weight>`"
        response_message = f"**Loras SDXL disponíveis:**\n{description}\n\n"
        chunks = list(self.split_list(self.loras_sdxl, 40))

        await interaction.response.send_message(f"{response_message}```\n{self.format_list(chunks[0])}\n```")

        for chunk in chunks[1:]:
            await interaction.followup.send(f"```\n{self.format_list(chunk)}\n```")

    @discord.app_commands.command(name="lora_sd1x", description="Lista todos os Loras SD 1.X disponíveis")
    async def lora_sd1x(self, interaction: discord.Interaction):
        if not self.loras_sd1x:
            await interaction.response.send_message("Nenhum Lora SD 1.X disponível no momento. Tente novamente mais tarde.")
            return

        description = "Uso geral dentro de um prompt: `<lora:LoraName:weight>`"
        response_message = f"**Loras SD 1.X disponíveis:**\n{description}\n\n"
        chunks = list(self.split_list(self.loras_sd1x, 40))

        await interaction.response.send_message(f"{response_message}```\n{self.format_list(chunks[0])}\n```")

        for chunk in chunks[1:]:
            await interaction.followup.send(f"```\n{self.format_list(chunk)}\n```")

    def format_list(self, items):
        """Formata a lista de itens como uma string com blocos de código."""
        return "\n".join(items)

    def split_list(self, items, n):
        """Divide a lista em sublistas de até n itens."""
        for i in range(0, len(items), n):
            yield items[i:i + n]

# Função de configuração para o Cog
async def setup(bot):
    await bot.add_cog(LorasModels(bot))

import discord
from discord.ext import commands
from discord import app_commands, Interaction, ui
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ouvrir un ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: Interaction, button: discord.ui.Button):
        modal = TicketModal()
        await interaction.response.send_modal(modal)

class TicketModal(ui.Modal, title="Créer un ticket"):
    raison = ui.TextInput(label="Raison du ticket", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True),
        }

        for member in guild.members:
            if member.guild_permissions.administrator:
                overwrites[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            reason="Ticket créé"
        )

        await channel.send(
            f"{interaction.user.mention} a ouvert un ticket.\n**Raison :** {self.raison}",
            view=CloseTicketButton()
        )
        await interaction.response.send_message(f"✅ Ton ticket a été créé ici : {channel.mention}", ephemeral=True)

class CloseTicketButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ Fermer le ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ Tu n'as pas la permission de fermer ce ticket.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commande(s) slash synchronisée(s).")
    except Exception as e:
        print(f"Erreur de sync : {e}")

@bot.tree.command(name="ticket_config", description="Configurer le système de tickets")
async def ticket_config(interaction: Interaction):
    await interaction.response.send_message("🎟️ Cliquez sur le bouton ci-dessous pour ouvrir un ticket :", view=TicketButton())

bot.run(TOKEN)

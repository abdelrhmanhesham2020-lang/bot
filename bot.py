import discord
from discord.ext import commands
import os

TOKEN = "PUT_YOUR_TOKEN_HERE"

intents = discord.Intents.default()
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Queue لكل سيرفر
queues = {}

# ---------------- ON READY ----------------
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"Logged in as {bot.user}")
    except Exception as e:
        print("Sync Error:", e)

# ---------------- JOIN ----------------
@bot.tree.command(name="join", description="يدخل الفويس")
async def join(interaction: discord.Interaction):
    await interaction.response.defer()

    member = interaction.guild.get_member(interaction.user.id)

    if member and member.voice and member.voice.channel:
        channel = member.voice.channel

        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        await channel.connect()
        await interaction.followup.send("🎧 دخلت الفويس")
    else:
        await interaction.followup.send("ادخل فويس الأول")

# ---------------- PLAY CORE ----------------
def play_next(vc, guild_id, songs):
    if guild_id not in queues:
        queues[guild_id] = songs.copy()

    if len(queues[guild_id]) == 0:
        queues[guild_id] = songs.copy()  # Loop

    next_song = queues[guild_id].pop(0)

    vc.play(
        discord.FFmpegPCMAudio(f"songs/{next_song}"),
        after=lambda e: play_next(vc, guild_id, songs)
    )

# ---------------- PLAY COMMAND ----------------
@bot.tree.command(name="play", description="تشغيل الصوت")
async def play(interaction: discord.Interaction):
    await interaction.response.defer()

    vc = interaction.guild.voice_client
    guild_id = interaction.guild.id

    if not vc:
        await interaction.followup.send("اعمل /join الأول")
        return

    if not os.path.exists("songs"):
        await interaction.followup.send("مفيش فولدر songs")
        return

    songs = os.listdir("songs")

    if len(songs) == 0:
        await interaction.followup.send("مفيش ملفات صوت")
        return

    if vc.is_playing():
        await interaction.followup.send("الصوت شغال بالفعل")
        return

    queues[guild_id] = songs.copy()

    first_song = queues[guild_id].pop(0)

    vc.play(
        discord.FFmpegPCMAudio(f"songs/{first_song}"),
        after=lambda e: play_next(vc, guild_id, songs)
    )

    await interaction.followup.send(f"🎵 شغال: {first_song}")

# ---------------- STOP ----------------
@bot.tree.command(name="stop", description="إيقاف وخروج")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()

    vc = interaction.guild.voice_client

    if vc:
        await vc.disconnect()
        await interaction.followup.send("⛔ خرجت")
    else:
        await interaction.followup.send("مش شغال أصلاً")

# ---------------- RUN ----------------
bot.run("MTQ2MzIyNDY5MzY3MzY4OTEwMA.GHI9g_.qxI5KhxmPIlOXJx1v4YUBoltDtZY3zd_EsV5jo")
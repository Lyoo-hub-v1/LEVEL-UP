import discord
from discord.ext import commands
import os
import json
import random
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

FILE_LEVEL = "level.json"
cooldown = {}

def load_data():
    try:
        with open(FILE_LEVEL, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(FILE_LEVEL, "w") as f:
        json.dump(data, f)

def xp_butuh_level(level):
    return 100 * (level ** 2)  # Level 1 butuh 100, Level 2 butuh 400, dst

@bot.event
async def on_ready():
    print(f"{bot.user} lah idup Dio!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.guild is None:
        return

    user_id = str(message.author.id)
    sekarang = time.time()

    # Biar dak spam XP, 1 menit 1x bae dapet XP
    if user_id in cooldown and sekarang - cooldown[user_id] < 60:
        await bot.process_commands(message)
        return
    
    cooldown[user_id] = sekarang
    data = load_data()
    
    if user_id not in data:
        data[user_id] = {"xp": 0, "level": 1}
    
    # Kasih XP random 10-20
    xp_dapet = random.randint(10, 20)
    data[user_id]["xp"] += xp_dapet
    
    level_sekarang = data[user_id]["level"]
    xp_butuh = xp_butuh_level(level_sekarang)

    # CEK NAIK LEVEL DAK?
    if data[user_id]["xp"] >= xp_butuh:
        data[user_id]["level"] += 1
        data[user_id]["xp"] = 0
        level_baru = data[user_id]["level"]
        
        await message.channel.send(f"🎉 **NAIK LEVEL DIO!** 🎉\n\nWOI! {message.author.mention} lah **NAIK KE LEVEL {level_baru}!**\nMakin sering chat, makin jago! Lanjutke Dio! 🔥🥚")

        # KASIH ROLE OTOMATIS DIO! - GANTI NAMA ROLE NYO
        # Kalo Level 5 dapet role SUHU, Level 10 dapet DEWA TELUR
        if level_baru == 5:
            role = discord.utils.get(message.guild.roles, name="SUHU")
            if role:
                await message.author.add_roles(role)
                await message.channel.send(f"😱 {message.author.mention} dapet role **SUHU**! Gilo!")
        if level_baru == 10:
            role = discord.utils.get(message.guild.roles, name="DEWA TELUR")
            if role:
                await message.author.add_roles(role)
                await message.channel.send(f"👑 {message.author.mention} dapet role **DEWA TELUR**! Raja nyo Steal An Egg!")

    save_data(data)
    await bot.process_commands(message)

@bot.command()
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    user_data = data.get(str(member.id), {"xp": 0, "level": 1})
    xp_butuh = xp_butuh_level(user_data["level"])
    await ctx.send(f"📊 **RANK {member.display_name}**\nLevel: **{user_data['level']}**\nXP: **{user_data['xp']} / {xp_butuh}**\nDikit lagi naik level Dio! Gas chat terus!")

@bot.command()
async def leaderboard(ctx):
    data = load_data()
    # Urutke dari level paling tinggi
    sorted_users = sorted(data.items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)[:10]
    
    teks = "🏆 **LEADERBOARD STEAL AN EGG** 🏆\n\n"
    for i, (user_id, info) in enumerate(sorted_users, 1):
        try:
            user = await bot.fetch_user(int(user_id))
            teks += f"{i}. {user.display_name} - Level {info['level']} ({info['xp']} XP)\n"
        except:
            pass
    
    if teks == "🏆 **LEADERBOARD STEAL AN EGG** 🏆\n\n":
        teks += "Belum ado yang chat Dio! Sepi nian!"
    
    await ctx.send(teks)

bot.run(os.getenv("DISCORD_TOKEN"))

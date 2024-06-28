import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
import pytz
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Definir intents
intents = discord.Intents.default()
intents.presences = True
intents.members = True

# Criar o bot com intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Dicionário para armazenar o status dos usuários
user_status = {}
start_time = time(6, 0, 0)  # 06:00 AM
end_time = time(22, 0, 0)   # 10:00 PM
timezone = pytz.timezone('America/Sao_Paulo')

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    track_status.start()
    daily_report_checker.start()
    weekly_report_checker.start()

@tasks.loop(minutes=1)
async def track_status():
    global user_status
    now = datetime.now(timezone).time()
    if start_time <= now <= end_time:
        for guild in bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue
                if member not in user_status:
                    user_status[member] = {"online": 0, "idle": 0, "dnd": 0, "offline": 0, "timestamps": []}
                status = str(member.status)
                user_status[member]["timestamps"].append((datetime.now(timezone), status))
                user_status[member][status] += 1

@tasks.loop(minutes=1)
async def daily_report_checker():
    now = datetime.now(timezone)
    if now.time() >= time(22, 0) and now.time() < time(22, 1):
        await send_report("daily")

@tasks.loop(minutes=1)
async def weekly_report_checker():
    now = datetime.now(timezone)
    if now.weekday() == 4 and now.time() >= time(22, 0) and now.time() < time(22, 1):
        await send_report("weekly")

async def send_report(report_type):
    now = datetime.now(timezone)
    if report_type == "daily":
        start_time = now - timedelta(days=1)
        period = "Relatório Diário"
    elif report_type == "weekly":
        start_time = now - timedelta(days=now.weekday() + 2)
        period = "Relatório Semanal"

    report = f"**{period} de Atividades dos Usuários**\n"
    for member, data in user_status.items():
        total_time_online = data["online"]
        total_time_idle = data["idle"]
        total_time_dnd = data["dnd"]
        report += f"\n**{member.display_name}**\n"
        report += f"🟢 **Online**: {total_time_online} minutos\n"
        report += f"🌙 **Ausente**: {total_time_idle} minutos\n"
        report += f"⛔ **Ocupado**: {total_time_dnd} minutos\n"
        report += f"Horários:\n"
        for timestamp, status in data['timestamps']:
            if timestamp > start_time:
                status_emoji = "🟢" if status == "online" else "🌙" if status == "idle" else "⛔" if status == "dnd" else "⚪"
                report += f"  {status_emoji} {timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {status}\n"
    
    # Enviar relatório no Discord
    channel = bot.get_channel(1256340479369412709)
    if channel:
        await channel.send(report)
    else:
        print("Canal não encontrado. Verifique se o ID do canal está correto.")

# Substitua 'YOUR_DISCORD_BOT_TOKEN' pelo token que você copiou
bot.run('MTI1NjMzNTc0MDYwMjY3OTM5OA.GC6oVf.mKl1N_Dm3ctCfUAs3j9bXu0RR1Xxj4NGeYX5fk')
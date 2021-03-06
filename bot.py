import os
import aiohttp
import json
import discord
from discord.ext import commands

DEBUG = os.getenv('DEBUG')

TOKEN = os.getenv('DISCORD_TOKEN')
if DEBUG:
    print(TOKEN)

COLOR_OK = 0x21ba45
COLOR_WARNING = 0xf7ac0a
COLOR_ERROR = 0xDB2828

bot = commands.Bot(command_prefix='~')

@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
    
    print("bot online in " + str(guild_count) + " servers")

@bot.command()
async def status(ctx):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        url = 'https://axie.zone:3000/server_status'

        # Delete message that triggered the command
        await ctx.message.delete()

        # Try and fetch data. If this returns an exception, it will call status_error()
        async with session.get(url) as resp:
            data = await resp.json(content_type=None)

            # Extract data from API response
            maintenance = data.get('status_maintenance', None)
            login = data.get('status_login', None)
            battles = data.get('status_battles', None)

            # Setup field messages
            maintenance_msg = 'Ongoing maintenance' if maintenance else 'No maintenance'
            login_msg = 'Online' if not login else 'Status unknown'
            battles_msg = 'Online' if battles > 2 else 'Status unknown'

            # Setup embed color
            color = COLOR_ERROR if maintenance else COLOR_WARNING if login or battles <= 2 else COLOR_OK

            # Generate embed
            embed = discord.Embed(title='Axie Infinity Game Server Status', color=color)
            embed.add_field(name='Maintenance', value=maintenance_msg, inline=False)
            embed.add_field(name='Login', value=login_msg, inline=False)
            embed.add_field(name='Battles', value=battles_msg, inline=False)

            # Send embed and delete after 20 minutes
            await ctx.send(embed=embed, delete_after=1200)

@status.error
async def status_error(ctx, error):
    if DEBUG:
        print(error)

    embed = discord.Embed(description='The server status checker service is currently unavailable!', color=COLOR_WARNING)
    await ctx.send(embed=embed, delete_after=5)

if __name__ == '__main__':
    bot.run(TOKEN)
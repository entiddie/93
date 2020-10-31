import discord
from discord.ext import commands
import os
import random
import time
import asyncio
import json


client = commands.Bot(command_prefix=commands.when_mentioned_or("+", "93 "), case_insensitive=True)

client.remove_command('help')


# ---- Cogs ----


@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")


# ---- Events ----


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="prefix +"))
    print('Logged in as {0} ({0.id})'.format(client.user))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description=f"Please pass in all requirements",
            color=0xff0000)
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description=f"You don't have the required permissions",
            color=0xff0000)
        await ctx.send(embed=embed)
    if isinstance(error, commands.CommandOnCooldown):
        coold = str(time.strftime('%H:%M:%S', time.gmtime(error.retry_after)))
        embed = discord.Embed(
            description=f"**{ctx.author}** Calm down! Try again in {coold}",
            color=0xff0000)
        await ctx.send(embed=embed)


async def get_afk_data():
    with open("afk.json", "r") as f:
        users = json.load(f)

    return users


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    users = await get_afk_data()

    if len(message.mentions) > 0:
        if message.mentions[0].id in users:
            channel = message.channel
            await channel.send(f"This user is AFK: {users[message.mentions[0].id]['status']}")
            

    await client.process_commands(message)


# ---- Basic Commands ----


@client.command()
async def hello(ctx):
    responses = ['Hello!', 'Hey!', "I'm here", 'Hello~']
    await ctx.send(f"{random.choice(responses)}")


@client.command()
async def ping(ctx):
    await ctx.send(f":ping_pong: Pong! {round(client.latency * 1000)}ms")


@client.command(aliases=['say'])
@commands.has_permissions(manage_messages=True)
async def repeat(ctx, *args):
    await ctx.send(' '.join(args))



client.run('')

import discord
from discord.ext import commands
import os
import random
import time
import asyncio
import json


client = commands.Bot(command_prefix=commands.when_mentioned_or("+", "93 "), case_insensitive=True, owner_id=353416871350894592)

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


client.blacklisted_users = []


# ---- Events ----


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="prefix <"))
    data = read_json("blacklisted")
    client.blacklisted_users = data["blacklistedUsers"]
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



# ---- Blacklisted ----

def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file, indent=4)


async def get_afk_data():
    with open("afk.json", "r") as f:
        users = json.load(f)

    return users


@client.event
async def on_message(message):

    users = await get_afk_data()

    userid = str(message.author.id)

    if message.author.id in client.blacklisted_users:
        return

    if message.author.bot:
      return

    if userid in users:
        del users[userid]

        with open("afk.json", "w") as f:
            json.dump(users, f)


        await message.channel.send(f"Welcome back {message.author.display_name}! I removed your AFK status")
        

    for x in users:
        if x in message.content.lower():
            await message.channel.send(f"{message.author.mention} this user has set their status to AFK — {users[x]['status']}")

    await client.process_commands(message)


# ---- Basic Commands ----


@client.command()
@commands.is_owner()
async def blacklist(ctx, user: discord.Member):
    
    try:
        if ctx.message.author.id == user.id:
            await ctx.send(f"You cannot blacklist yourself!")

        client.blacklisted_users.append(user.id)
        data = read_json("blacklisted")
        data['blacklistedUsers'].append(user.id)
        write_json(data, "blacklisted")
        await ctx.send(f"I added {user} to the global blacklist")

    except:
        await ctx.send(f"Couldn't blacklist user")


@client.command()
@commands.is_owner()
async def whitelist(ctx, user: discord.Member):
    try:
        if ctx.message.author.id == user.id:
                await ctx.send(f"You cannot whitelist yourself!")

        client.blacklisted_users.remove(user.id)
        data = read_json("blacklisted")
        data['blacklistedUsers'].remove(user.id)
        write_json(data, "blacklisted")
        await ctx.send(f"I removed {user} from the global blacklist")
    except:
        await ctx.send(f"Couldn't whitelist user")


@client.command()
async def hello(ctx):
    responses = ['Hello!', 'Hey!', "I'm here", 'Hello~']
    await ctx.send(f"{random.choice(responses)}")


@client.command()
async def ping(ctx):
    before = time.monotonic()
    message = await ctx.send(":ping_pong: Pong!")
    ping = (time.monotonic() - before) * 1000
    await message.edit(content=f":ping_pong: Pong! `{int(ping)}ms`")


@client.command(aliases=['say'])
@commands.has_permissions(manage_messages=True)
async def repeat(ctx, *args):
    await ctx.send(' '.join(args))



client.run('')

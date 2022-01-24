import os
import discord
from discord.ext import commands, tasks
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
import random
import asyncio
import string
from captcha.image import ImageCaptcha
import pyrebase

#secret variables
discordToken = os.environ['discordToken']

#firebase secret vars
fapiKey = os.environ['fapiKey']
fauthDomain = os.environ['fauthDomain']
fdbURL = os.environ['fdbURL']
fprojectId = os.environ['fprojectId']
fstorageBucket = os.environ['fstorageBucket']
fmsgSenderId = os.environ['fmsgSenderId']
fappId = os.environ['fappId']
measureId = os.environ['measureId']

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return "Your Bot Is Ready"

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  server = Thread(target=run)
  server.start()

keep_alive()

image = ImageCaptcha(width = 280, height = 90)

#pyrebase
config = {
  "apiKey": fapiKey,
  "authDomain": fauthDomain,
  "databaseURL": fdbURL,
  "projectId": fprojectId,
  "storageBucket": fstorageBucket,
  "messagingSenderId": fmsgSenderId,
  "appId": fappId,
  "measurementId": measureId
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

client = commands.Bot(command_prefix = '$')

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity=discord.Game(name="$help"))

#Delete user messages in verify channel
@client.event
async def on_message(message):
    await client.process_commands(message)

    #Check if message was sent by bot, if yes return
    if message.author == client.user:
      return

    #Tries to get verify channel id
    try:
      channel = discord.utils.get(message.guild.channels, name="verify")
      channel_id = channel.id
      channelSent = message.channel.id
    
      if channelSent == channel_id:
        await message.delete()
    except:
      print("verify channel does not exist")

@client.command(pass_context=True)
async def verify(ctx):
  usersplitted = str(ctx.author).split("#")
  vuser = usersplitted[0] + ":" + usersplitted[1]
  linkuser = ''
    
  splittedlinkvuser = vuser.split(" ")
  linkuser = ''
  for i in splittedlinkvuser:
    if linkuser == '':
      linkuser = i
    else:
      linkuser = linkuser + '%' + i
  try:
    print(linkuser)
    if len(db.child("verified").child(linkuser).get().val()) == 0:
      await ctx.author.send("https://jerrybot-fa77f.web.app/?user=" + linkuser)
    else:
      member = ctx.author
      var = discord.utils.get(ctx.guild.roles, name = "isHuman")
      await member.add_roles(var)
      await ctx.author.send("u verified")
  except:
    await ctx.author.send("https://jerrybot-fa77f.web.app/?user=" + linkuser)
  
@client.command()
async def hello(ctx):
  await ctx.send('hi')
  return

@client.command()
async def say(ctx, thingToSay):
  await ctx.send(thingToSay)
  await ctx.message.delete()

@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
  await member.kick(reason=reason)
  await ctx.send(f'User {member} has been thrown out of the server')

@kick.error
async def kick_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("LOL Imagine not having permission to kick members... Imagine")

@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
  await member.ban(reason=reason)
  await ctx.send(f'You swung your ban hammer at {member}')

@ban.error
async def ban_error(ctx, error):

  if "50013" in str(error):
    await ctx.send("The person you tried to ban is too powerful...")
  
  if isinstance(error, commands.MissingPermissions):

    responses_list = ["You don't own a ban hammer dummy", "You swung your ban hammer AND MISSED! You can't even swing straight..."]

    responseNO = random.randint(0, len(responses_list))

    await ctx.send(responses_list[responseNO])

@client.command()
@has_permissions(ban_members=True)
async def unban(ctx, *, member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split('#')

  for ban_entry in banned_users:
    user = ban_entry.user

    if(user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f"Unbanned {user.name}#{user.discriminator}")

@unban.error
async def unban_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("LOL imagine not having perms to unban someone... Imagine")

#setups
@client.command(pass_context=True)
async def setup(ctx, setupChoice):
  print(str(setupChoice))
  if str(setupChoice) == "verify":
    print("hello")
    channel = await ctx.guild.create_text_channel("verify")
    
    await channel.send("Verify that you are human by typing $verify")

    guild = ctx.guild
    await guild.create_role(name="isHuman")

    await ctx.send("Verify Has Been Setup")
  
client.run(discordToken)
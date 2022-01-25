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
import requests
from discord import Webhook, RequestsWebhookAdapter
from flask import Flask
from threading import Thread


#secret variables
discordToken = os.environ['discordToken']
logsWebhook = os.environ['logsWebhookURL']

#firebase secret vars
fapiKey = os.environ['fapiKey']
fauthDomain = os.environ['fauthDomain']
fdbURL = os.environ['fdbURL']
fprojectId = os.environ['fprojectId']
fstorageBucket = os.environ['fstorageBucket']
fmsgSenderId = os.environ['fmsgSenderId']
fappId = os.environ['fappId']
measureId = os.environ['measureId']

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

client = commands.Bot(command_prefix = '$', help_command=None)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity=discord.Game(name="$help"))

#Delete user messages in verify channel
#muted
@client.event
async def on_message(message):
    ctx = await client.get_context(message)

    if ctx.valid:
      webhook = Webhook.from_url(logsWebhook, adapter=RequestsWebhookAdapter())
      webhook.send(f'{message.author} sent: {message.content}')

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

    role = discord.utils.get(message.guild.roles, name="visually muted")
    if role in message.author.roles:
        await message.delete()
    else:
      return

@client.command()
async def help(ctx):

  embedVar = discord.Embed(title="Commands", description="The commands. Prefix: `$`", color=0x00ff00)
  embedVar.add_field(name="$help", value="Aids you with commands. Syntax: `$help`", inline=False)
  embedVar.add_field(name="$setup", value="setup something. Type `$setup help` for more info. Syntax: `$setup <thing to setup>", inline=False)
  embedVar.add_field(name="$mute", value="mute an annoying user. Syntax: `$mute <user> <reason>`", inline=False)
  embedVar.add_field(name="$unmute", value="unmute an annoying user and regret it. Syntax: `$unmute <user> <reason>`", inline=False)
  embedVar.add_field(name="$ban", value="Swing your ban hammer at someone Syntax: `$ban <user> <reason>`", inline=False)
  embedVar.add_field(name="$unban", value="Forgive one of your enemies then and regret it. Syntax: `$unban <user>`", inline=False)
  embedVar.add_field(name="$kick", value="Throw someone out of your server. Syntax: `$kick <user> <reason>`", inline=False)
  embedVar.add_field(name="$say", value="Make me say something. Syntax: `$say <thing to say>`", inline=False)
  embedVar.add_field(name="$hello", value="Make me greet you. Syntax: `$hello`", inline=False)
  embedVar.add_field(name="$verify", value="Verify that you are indeed human. The admin must first setup verify with `$setup verify`. Syntax: `$verify`", inline=False)
  embedVar.add_field(name="NOTE", value="ALL commands used would be logged into another server. By using this bot, you consent every single command you use to be logged onto another server for moderation purposes. Unless its necessary, the logs would not be shared publicly.", inline=False)
  await ctx.send(embed=embedVar)


@client.command(pass_context=True)
@commands.has_role('staff')
async def mute(ctx, member: discord.Member, *, reason=None):
  var = discord.utils.get(ctx.guild.roles, name = "visually muted")
  await member.add_roles(var)
  await ctx.send(f'{member} has been muted')

@mute.error
async def mute_error(ctx, error):
  if isinstance(error, commands.MissingRole):
    await ctx.send("You are not strong enough to mute people LOL")
  else:
    await ctx.send("An unknown error occured")

@client.command(pass_context=True)
@commands.has_role('staff')
async def unmute(ctx, member: discord.Member, *, reason=None):
  try:
    role = discord.utils.get(ctx.guild.roles, name = "visually muted")
    await member.remove_roles(role)
    await ctx.send(f'{member} has been unmuted')
  except:
    ctx.send(f'{member} is not muted')

@unmute.error
async def unmute_error(ctx, error):
  if isinstance(error, commands.MissingRole):
    await ctx.send("You are not strong enough to unmute people LOL")
  else:
    await ctx.send("An unknown error occured")

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
async def say(ctx, *thingToSay):
  thingToSayFormatted = ''
  for i in thingToSay:
    if thingToSayFormatted == '':
      thingToSayFormatted = i
    else:
      thingToSayFormatted = thingToSayFormatted + " " + i

  await ctx.send(thingToSayFormatted)
  await ctx.message.delete()

@client.command()
@commands.has_role('staff')
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

@client.command(pass_context=True)
@commands.has_role('staff')
async def delete(ctx, id):
  await ctx.message.delete()
  msg = await ctx.fetch_message(id)
  await msg.delete()
  await ctx.author.send(f'message id: {id} has been deleted')
  
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
  
  if str(setupChoice) == "mute":
    guild = ctx.guild
    await guild.create_role(name="visually muted")
    await ctx.send("Mute has been setup!")
  
  if str(setupChoice) == "perms":
    guild = ctx.guild
    await guild.create_role(name="staff")
    await ctx.send("Permissions have been setup! Add the staff role to anyone who is a mod")
  
  if str(setupChoice) == "help":
    setuphelpembed = discord.Embed(title="Setup command", description="Syntax: `$setup <thing to setup>`", color=0x00ff00)
    setuphelpembed.add_field(name="$setup verify", value="Setup verification. Syntax: `$setup verify`", inline=False)
    setuphelpembed.add_field(name="$setup mute", value="Setup a system to make people shut up Syntax: `$setup mute`", inline=False)
    setuphelpembed.add_field(name="$setup perms", value="Setup permissions. You must do this if you want to be able to mute people. Syntax: `$setup perms`", inline=False)
    await ctx.send(embed=setuphelpembed)

  
client.run(discordToken)
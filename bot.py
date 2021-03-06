from dotenv import load_dotenv
import os
import discord
from discord.ext import commands

load_dotenv()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Connecté en tant que {0.user}'.format(bot))

""" @client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')
 """

@bot.command()
async def test(ctx):
    print("Reçu")
    await ctx.send("Test ok")

@bot.command(name='createPronom')
async def createPronoun(ctx, *pronouns):
    if len(pronouns) < 1:
        await ctx.send('Le pronom n\'a pas été spécifié')
        return
    singlePronoun = pronouns[0]
    try:
        await ctx.guild.create_role(name='Pronom : {0}'.format(singlePronoun), hoist=False, mentionable=False, reason='Créé le rôle "Pronom : {0}" via le bot'.format(singlePronoun))
        await ctx.send('Le rôle {0} a été créé'.format(singlePronoun))
    except discord.Forbidden:
        await ctx.send('Problème de permissions du bot pour la création d\'un rôle')
    except (discord.HTTPException, discord.InvalidArgument) as e:
        await ctx.send('Erreur lors de la création du rôle\nDétails de l\'erreur : \n`{0}`'.format(e))
    

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        print('{0} : {1}'.format(type(error), error))

bot.run(os.getenv('TOKEN'))
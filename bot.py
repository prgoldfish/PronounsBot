from dotenv import load_dotenv
import os
from pathlib import Path
import discord
import logging
from discord.ext import commands

load_dotenv()

bot = commands.Bot(command_prefix='!')

goldfishMention = '<@!{0}>'.format(os.getenv('GOLDFISH_ID'))

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] : %(filename)s:%(lineno)d %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

async def checkLogSize():
    if(Path('./bot.log').stat().st_size >= 512 * 1024 * 1024):
        goldfish = await bot.fetch_user(int(os.getenv('GOLDFISH_ID')))
        await goldfish.send('Va vider le mon fichier de log !')


@bot.event
async def on_ready():
    logging.info('Connecté en tant que %s', bot.user)
    await checkLogSize()
    print('Connecté')


@bot.command()
async def test(ctx):
    logging.info('Reçu')
    await ctx.send('> Test ok.')

@bot.command(name='createPronom')
async def createPronoun(ctx: commands.Context, *pronouns):
    if len(pronouns) < 1:
        await ctx.send('> Le pronom n\'a pas été spécifié')
        return
    singlePronoun = pronouns[0].capitalize()
    try:
        await ctx.guild.create_role(name='Pronom : {0}'.format(singlePronoun), hoist=False, mentionable=False, reason='Créé le rôle "Pronom : {0}" via le bot'.format(singlePronoun))
        await ctx.send('> Le rôle `Pronom : {0}` a été créé'.format(singlePronoun))
    except discord.Forbidden:
        await ctx.send('> Problème de permissions du bot pour la création d\'un rôle')
    except (discord.HTTPException, discord.InvalidArgument) as e:
        await ctx.send('> Erreur lors de la création du rôle\n{0}, va régler ça !'.format(goldfishMention))
        logging.exception('Erreur lors de la création du rôle\nDétails de l\'erreur : \n%s', e)
    
@bot.command(name='ajoutPronom')
async def addPronoun(ctx: commands.Context, *pronouns):
    if len(pronouns) < 1:
        await ctx.send('> Le pronom n\'a pas été spécifié')
        return
    author = ctx.author
    response = ''
    for singlePronoun in map(str.capitalize, pronouns):
        role = next(filter(lambda r: r.name == 'Pronom : {0}'.format(singlePronoun), ctx.guild.roles), None)
        if role != None:
            if len([r for r in author.roles if r.name == role.name]) > 0:
                response += '> Vous avez déjà le rôle correspondant à `{0}`\n'.format(singlePronoun)
            else:
                try:
                    await author.add_roles(role, reason='Ajout du rôle "{0}" pour {1} via le bot'.format(role.name, author.name))
                    response += '> Vous avez maintenant le rôle `{0}`\n'.format(role.name)
                except discord.Forbidden:
                    response += '> Problème de permissions du bot pour l\'assignation d\'un rôle\n'
                except discord.HTTPException as e:
                    response += '> Erreur lors de l\'assignation du rôle\n{0}, va régler ça !'.format(goldfishMention)
                    logging.exception('Erreur lors de l\'assignation du rôle\nDétails de l\'erreur : \n%s', e)
        else:
            response += '> Le pronom `{0}` n\'existe pas en tant que rôle sur le serveur. Demandez à un.e modérateur.ice de l\'ajouter\n'.format(singlePronoun)
    await ctx.send(response)

@bot.command(name='enleverPronom')
async def removePronoun(ctx: commands.Context, *pronouns):
    if len(pronouns) < 1:
        await ctx.send('> Le pronom n\'a pas été spécifié')
        return
    author = ctx.author
    response = ''
    for singlePronoun in map(str.capitalize, pronouns):
        role = next(filter(lambda r: r.name == 'Pronom : {0}'.format(singlePronoun), ctx.guild.roles), None)
        if role != None:
            if len([r for r in author.roles if r.name == role.name]) == 0:
                response += '> Vous n\'avez pas le rôle correspondant à `{0}`\n'.format(singlePronoun)
            else:
                try:
                    await author.remove_roles(role, reason='Enlevé le rôle "{0}" pour {1} via le bot'.format(role.name, author.name))
                    response += '> Le rôle `{0}` a bien été enlevé\n'.format(role.name)
                except discord.Forbidden:
                    response += '> Problème de permissions du bot pour la suppression d\'un rôle\n'
                except discord.HTTPException as e:
                    response += '> Erreur lors de la suppression du rôle\n{0}, va régler ça !'.format(goldfishMention)
                    logging.exception('Erreur lors de la suppression du rôle\nDétails de l\'erreur : \n%s', e)
        else:
            response += '> Le pronom `{0}` n\'existe pas en tant que rôle sur le serveur\n'.format(singlePronoun)
    await ctx.send(response)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        print('{0} : {1}'.format(type(error), error))
        logging.exception('%s : %s', type(error), error)



bot.run(os.getenv('TOKEN'))
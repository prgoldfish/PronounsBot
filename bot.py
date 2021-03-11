from dotenv import load_dotenv
import os
from pathlib import Path
import discord
import logging
from discord.ext import commands

listePronoms = ('il', 'elle', 'iel', 'yel', 'ielle', 'al', 'ol', 'olle', 'ul', 'ulle', 'ael', 'ille', 'el', 'i', 'im')

load_dotenv()

bot = commands.Bot(command_prefix='!')

goldfishMention = '<@!{0}>'.format(os.getenv('GOLDFISH_ID'))

awaitingConfirm = False

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] : %(filename)s:%(lineno)d %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

def getPronounRole(ctx, singlePronoun):
    return next(filter(lambda r: r.name == 'Pronom : {0}'.format(singlePronoun), ctx.guild.roles), None)

async def checkLogSize():
    if(Path('./bot.log').stat().st_size >= 512 * 1024 * 1024):
        goldfish = await bot.fetch_user(int(os.getenv('GOLDFISH_ID')))
        await goldfish.send('Va vider mon fichier de log !')


@bot.check
async def noDM(ctx):
    return ctx.guild != None

@bot.event
async def on_ready():
    await checkLogSize()
    logging.info('Connecté en tant que %s', bot.user)
    print('Connecté')


@bot.command('installerPronoms')
@commands.has_permissions(manage_roles=True)
async def confirm(ctx, *args):
    global awaitingConfirm
    awaitingConfirm = True
    await ctx.send('> Attention ! Cette commande va installer jusqu\'à {0} rôles sur le serveur. Faites `!oui` pour confirmer ou `!non` pour annuler'.format(len(listePronoms)))

@bot.command('oui')
@commands.has_permissions(manage_roles=True)
async def install(ctx, *args):
    global awaitingConfirm
    if awaitingConfirm:
        awaitingConfirm = False
        for sp in list(filter(lambda p : getPronounRole(ctx, p) == None, listePronoms)):
            await createPronoun(ctx, sp)
        await ctx.send('> Installation terminée')
    else:
        await ctx.send('> Aucune commande à confirmer')

@bot.command('non')
@commands.has_permissions(manage_roles=True)
async def cancel(ctx, *args):
    global awaitingConfirm 
    if awaitingConfirm:
        awaitingConfirm = False
        await ctx.send('> Installation annulée')
    else:
        await ctx.send('> Aucune commande à annuler')

@bot.command()
@commands.is_owner()
async def test(ctx):
    logging.info('Reçu')
    await ctx.send('> Test ok.')

@bot.command(name='createPronom')
@commands.has_permissions(manage_roles=True)
async def createPronoun(ctx: commands.Context, *pronouns):
    if len(pronouns) < 1:
        await ctx.send('> Le pronom n\'a pas été spécifié')
        return
    singlePronoun = pronouns[0].capitalize()
    if getPronounRole(ctx, singlePronoun) != None:
        await ctx.send('> Le rôle `Pronom : {0}` existe déjà'.format(singlePronoun))
        return
    try:
        await ctx.guild.create_role(name='Pronom : {0}'.format(singlePronoun), hoist=False, mentionable=False, reason='Créé le rôle "Pronom : {0}" via le bot'.format(singlePronoun))
        await ctx.send('> Le rôle `Pronom : {0}` a été créé'.format(singlePronoun))
    except discord.Forbidden:
        await ctx.send('> Problème de permissions du bot pour la création d\'un rôle')
    except (discord.HTTPException, discord.InvalidArgument) as e:
        await ctx.send('> Erreur lors de la création du rôle\n{0}, va régler ça !'.format(goldfishMention))
        logging.exception('Erreur lors de la création du rôle\nDétails de l\'erreur : \n%s', e)
""" 
@createPronoun.error
async def createPronoun_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('> Vous n\'avez pas la permission d\'ajouter des pronoms.') """
    
@bot.command(name='ajoutPronom')
async def addPronoun(ctx: commands.Context, *pronouns):
    if len(pronouns) < 1:
        await ctx.send('> Le pronom n\'a pas été spécifié')
        return
    author = ctx.author
    response = ''
    for singlePronoun in map(str.capitalize, pronouns):
        role = getPronounRole(ctx, singlePronoun)
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
        role = getPronounRole(ctx, singlePronoun)
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

@bot.command(name='aidePronom')
async def help(ctx, *args):
    response = '> `!aidePronom` Affiche cette aide\n'
    response += '> `!createPronom [pronom]` Crée un rôle correspondant à [pronom] (Utilisable seulement par les personnes pouvant gérer des rôles)\n'
    response += '> `!installerPronoms` Installe une liste prédéfinie de pronoms (Utilisable seulement par les personnes pouvant gérer des rôles)\n'
    response += '> `!ajoutPronom [pronom1] [pronom2] ...` Vous ajoute les rôles correspondant aux pronoms renseignés (si ces rôles existent)\n'
    response += '> `!enleverPronom [pronom1] [pronom2] ...` Vous enlève les rôles correspondant aux pronoms renseignés (si ces rôles existent)\n'
    await ctx.send(response)
    

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('> Vous n\'avez pas la permission d\'utiliser cette commande')
    else:
        print('{0} : {1}'.format(type(error), error))
        logging.exception('%s : %s', type(error), error)



bot.run(os.getenv('TOKEN'))

#TODO: Faire permissions pour les commandes -ok
#TODO: Package de base de pronoms + installation en 1 commande -ok
#TODO: Ecoute sur un channel précis ?
#TODO: Commandes inutiles/débiles
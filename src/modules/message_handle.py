"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""

import re, traceback
from modules import config
from discord.ext import commands
from discord import utils, AllowedMentions, Embed, errors, Message, TextChannel
from ext import Database
db = Database()
dbc = db.dbc
#########################################################
################ GROUP SYSTEM ###########################
#########################################################


def get_slot(ms:Message):
    for i in range(1, 13):
        if f"{i})" not in ms.content:return f"{i})"


async def process_registration_group(group:int,  grpc:TextChannel, bot:commands.Bot, msg:Message, totalSlot:int):
    """This function is basically a helper for managing automated group system. but there is a problem of customization.
    this function can manage group system for any group of 12 teams. which is kind of a limitation. but it can be customized!!
    i've not yet customised this function. but if you wanna customise it, you're welcome!!
    
    Parameters
    -----------
    
    group : int
        Group Number
    
    grpc : TextChannel
        Group Channel
        
    bot : commands.Bot
        Bot Object
        
    msg : Message
        Message Object
        
    totalSlot : int
        Total Slot
    
    Returns
    --------
    Coroutine[Any, Any, Message] | None (basically None)"""

    messages:list[Message] = [message async for message in grpc.history(limit=totalSlot)]

    for ms in messages:
        if len(messages) <3:
            if ms.author.id != bot.user.id:
                if f"**__GROUP__ {str(group)} **" not in ms.content:
                    await grpc.send(f"**__GROUP__ {group} ** \n{get_slot(ms)} {msg}")
        if ms.author.id == bot.user.id:
            if f"**__GROUP__ {str(group)} **" in ms.content:
                if "12)" not in ms.content.split():
                    cont = f"{ms.content}\n{get_slot(ms)} {msg}"
                    return await ms.edit(content=cont)
                if "12)" in ms.content.split():pass
            if f"**__GROUP__ {str(group)} **" not in ms.content:
                ms = await grpc.send(f"**__GROUP__ {group} ** \n")
                cont = f"{ms.content}\n{get_slot(ms=ms)} {msg}"
                return await ms.edit(content=cont)
    if len(messages) < 1:
        ms = await grpc.send(f"**__GROUP__ {group} ** \n")
        cont = f"{ms.content}\n{get_slot(ms)} {msg}"
        return await ms.edit(content=cont)

def get_group(reged:int):
    """Returns Group Number Based On Registered Teams

    Parameters
    -----------
    reged : int
    
    Returns
    --------
    str"""
    grp = reged/12
    if grp > int(grp):grp = grp + 1
    return str(int(grp))

async def auto_grp(message:Message, bot:commands.Bot):
    try:td = dbc.find_one({"cch":message.channel.id})
    except Exception:return
    if td:
        if td["auto_grp"] == "yes":
            if message.author.id == bot.user.id:
                if not message.embeds:return
                if message.embeds:
                    if "TEAM NAME" not in message.embeds[0].description:return
                reged = td["reged"]-1
                grpch = utils.get(message.guild.channels, id=int(td["gch"]))
                group = get_group(reged=reged)
                return await process_registration_group(group=group, grpc=grpch, bot=bot, msg=message.content, totalSlot=td["tslot"])

##########################################################################
########################### SLOT CONFIRM SYSTEM ##########################
##########################################################################
def gp(info:str):
    match = ["INR", "inr" , "₹", "Inr", "$"]
    for i in match:
        if i in info:
            ad =  info.split(i)[0].split()[-1]
            return f"{ad} {i}"
        else:return "No Data"

async def get_prize(cch:TextChannel):
    info = cch.category.channels[0]
    finder = ["Prize", "prize", "PRIZE", "POOL", "Pool", "PrizE"]
    messages = [message async for message in info.history(limit=123)]
    if len(messages) == 0:return "No Data Given"
    for i in messages:
        for p in finder:
            if p in str(i.content).split():return gp(info=i.content)
            else:return "No Data"

def find_team(message:Message):
    content = message.content.lower()
    teamname = re.search(r"team.*", content)
    if teamname is None:return f"{message.author}'s team"
    teamname = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", teamname.group()).strip()
    teamname = f"{teamname.title()}" if teamname else f"{message.author}'s team"
    return teamname

def reg_update(message:Message):
    df = dbc.find_one({"rch" : message.channel.id})
    rgd = df["reged"] 
    dbc.update_one({"rch" : message.channel.id}, {"$set":{"reged": rgd + 1}})


#Fake Tag Check
async def ft_ch(message:Message):
    ctx = message
    messages = [message async for message in ctx.channel.history(limit=123)]  
    for fmsg in messages:
        if fmsg.author.id != ctx.author.id:
            for mnt in fmsg.mentions:
                if mnt in message.mentions:return mnt
    return None

#Tourney System
async def tourney(message:Message):
    if message.author.bot:return
    if not message.guild:return
    ctx = message
    guild = message.guild
    tmrole = utils.get(ctx.guild.roles, name="tourney-mod")
    if tmrole in ctx.author.roles:return
    td = dbc.find_one({"rch" : message.channel.id})
    if td is None:return
    if td["status"] == "paused":await message.author.send("Registration Paused")
    if td is not None and message.channel.id  == int(td["rch"]) and td["status"] == "started":
        messages = [message async for message in ctx.channel.history(limit=2000)]
        crole = utils.get(guild.roles, id=int(td["crole"]))
        cch = utils.get(guild.channels, id = int(td["cch"]))
        rch = utils.get(guild.channels, id = int(td["rch"]))
        ments = td["mentions"]
        rgs = td["reged"]
        tslot = td["tslot"]
        if not crole:
            try:await message.author.send("Registration Paused")
            except Exception:pass
            await ctx.reply("Confirm Role Not Found")
            return dbc.update_one({"rch" : ctx.channel.id}, {"$set" : {"status" : "paused"}})
        if crole in message.author.roles:
            try:await message.delete()
            except Exception:pass
            return await message.channel.send("**Already Registered**", delete_after=5)
        if rgs > tslot:
            overwrite = rch.overwrites_for(message.guild.default_role)
            overwrite.update(send_messages=False)
            await rch.set_permissions(guild.default_role, overwrite=overwrite)
            await message.delete()
            return await rch.send("**Registration Closed**")
        elif len(message.mentions) >= ments:
            for fmsg in messages:
                
                #IF FAKE TAG NOT ALLOWED
                ########################
                if td["faketag"] == "no":
                    if fmsg.author.id == ctx.author.id and len(messages) == 1:
                        await message.add_reaction("✅")
                        reg_update(message)
                        team_name = find_team(message)
                        femb = Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                        femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                        femb.timestamp = message.created_at
                        femb.set_thumbnail(url=message.author.display_avatar)
                        await cch.send(f"{team_name.upper()} {message.author.mention}", embed=femb)
                        await message.author.add_roles(crole)
                        if rgs >= tslot*0.1 and td["pub"] == "no":
                            dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                    if fmsg.author.id != ctx.author.id:
                        ftch = await ft_ch(message)
                        if ftch != None:
                            fakeemb = Embed(title=f"The Member  {ftch}, You Tagged is Already Registered In A Team. If You Think He Used `Fake Tags`, You can Contact `Management Team`", color=0xffff00)
                            fakeemb.add_field(name="Team", value=f"[Registration Link]({fmsg.jump_url})")
                            fakeemb.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                            if message: await message.delete()
                            return await ctx.channel.send(embed=fakeemb, delete_after=60)
                        if ftch == None:
                            try:
                                await message.author.add_roles(crole)
                                await message.add_reaction("✅")
                                reg_update(message)
                                team_name = find_team(message)
                                femb = Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                                femb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                                femb.timestamp = message.created_at   
                                femb.set_thumbnail(url=message.author.display_avatar)
                                if rgs >= tslot*0.1 and td["pub"] == "no":
                                    dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                                return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=femb)
                            except Exception as e:print(e)
                                
                #IF FAKE TAG ALLOWED
                ####################
                if td["faketag"] == "yes":
                    await message.author.add_roles(crole)
                    await message.add_reaction("✅")
                    reg_update(message)
                    team_name = find_team(message)
                    nfemb = Embed(color=0xffff00, description=f"**{rgs}) TEAM NAME: [{team_name.upper()}]({message.jump_url})**\n**Players** : {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention} ")
                    nfemb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                    nfemb.timestamp = message.created_at
                    nfemb.set_thumbnail(url=message.author.display_avatar)
                    if rgs >= tslot*0.1 and td["pub"] == "no":
                        dbc.update_one({"rch" : td["rch"]}, {"$set" : {"pub" : "yes", "prize" : await get_prize(cch)}})
                    return await cch.send(f"{team_name.upper()} {message.author.mention}", embed=nfemb)
        elif len(message.mentions) < ments:
            meb = Embed(description=f"**Minimum {ments} Mentions Required For Successfull Registration**", color=0xff0000)
            try:await message.delete()
            except Exception as e:print(f"line No 335, error: {e}")
            return await message.channel.send(content=message.author.mention, embed=meb, delete_after=5)

################# NITROF ######################
async def nitrof(message:Message, bot:commands.Bot):
    if message.author.bot:return
    try:gnitro = db.guildbc.find_one({"guild_id" : message.guild.id})
    except Exception:return
    if gnitro != None and gnitro["nitro"] == "enabled":
        try:webhook = utils.get(await message.channel.webhooks(), name="Spruce")
        except Exception:await message.reply("Nitro Module Enabled But Missing Permissions - `manage_messages` , `manage_webhooks`")
        if not webhook:
            try:webhook = await message.channel.create_webhook(name="Spruce")
            except Exception:await message.reply("Missing Permissions - `manage_messages` , `manage_webhooks`")
        words = message.content.split()
        for word in words:
            if word[0] == ":" and word[-1] == ":":
                emjn = word.replace(":", "")
                emoji = utils.get(bot.emojis, name=emjn)
                if emoji != None:
                    if emoji.name in message.content:
                        msg1 = message.content.replace(":","").replace(f"{emoji.name}" , f"{emoji}")
                        allowed_mentions = AllowedMentions(everyone = False, roles=False, users=True)
                        nick = message.author.nick
                        if message.author.nick == None:
                            nick = message.author.name
                        await message.delete()
                        return await webhook.send(avatar_url=message.author.display_avatar, content=msg1, username=nick, allowed_mentions= allowed_mentions)
    else:return

############## ERROR HANDEL ################
############################################
async def error_handle(ctx:commands.Context, error:errors.DiscordException, bot:commands.Bot):
    erl = bot.get_channel(config.erl)
    cmdnf = bot.get_channel(config.cmdnf)
    try:
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=Embed(color=0xff0000, description=f"Missing Required Arguments! You Should Check How To Use This Command.\nTip: use `{config.prefix}help {ctx.command.name}` to get Instructions"))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=Embed(color=0xff0000, description="You don't have Permissions To Use This Command"))
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(embed=Embed(color=0xff0000, description="This Command Is Currently Disabled! You Can Try Again Later"))
        elif isinstance(error, commands.CommandNotFound):
            await cmdnf.send(f"```py\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\nCommand : {ctx.message.content}```")
            # return await ctx.send(embed=Embed(color=0xff0000, description="Command Not Found! Please Check Spelling Carefully."))
        elif isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))
        elif isinstance(error, commands.UserInputError):
            return await ctx.send(embed=Embed(color=0xff0000, description="Please Enter Valid Arguments"))
        elif isinstance(error, commands.EmojiNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Emoji Not Found"))
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=Embed(color=0xff0000, description="This Is A Owner Only Command You Can't Use It"))
        elif isinstance(error, commands.MessageNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Message Not Found Or Deleted"))
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Member Not Found"))
        elif isinstance(error, commands.ChannelNotFound):
            return await ctx.send(embed=Embed(color=0xff0000, description="Channel Not Found"))
        elif isinstance(error, commands.GuildNotFound):
            return await ctx.send("**I'm Not In The Server! which You Want To See**", delete_after=19)
        elif isinstance(error, commands.ChannelNotReadable):
            return await ctx.send(embed=Embed(color=0xff0000, description="Can Not Read Messages Of The Channel"))
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))
        elif "Manage Messages" in str(error):
            return await ctx.send(embed=Embed(description="Missing `Manage Messages` Permission", color=0xff0000))
        elif "Unknown file format." in str(error):
            return await ctx.send(embed=Embed(description="Invalid Input", color=0xff0000))
        elif "Send Messages" in str(error):
            return await ctx.author.send(embed=Embed(description=f"I don't have Permissions To Send message in this channel - {ctx.channel.mention}", color=0xff0000))
        elif "This playlist type is unviewable." in str(error):
            return await ctx.send(embed=Embed(description="This playlist type is unsupported!", color=0xff0000))
        elif "Maximum number of channels in category reached (50)" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of channels in category reached (50)", color=0xff0000), delete_after=30)
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(embed=Embed(color=0xff0000, description=str(error)))
        elif "error code: 10003" in str(error):
            return await ctx.send(embed=Embed(description="Channel Deleted Or Invalid", color=0xff0000))
        elif "error code: 50013" in str(error):
            return await ctx.send(embed=Embed(description="**Missing Permissions! You Should Check My Permissions**", color=0xff0000), delete_after=30)
        elif "Unknown Role" in str(error):
            return await ctx.send(embed=Embed(description="**Given Role Is Invalid Or Deleted**", color=0xff0000), delete_after=30)
        elif "Cannot delete a channel required for community servers" in str(error):
            return await ctx.send(embed=Embed(description="**I Cannot delete a channel required for community servers**", color=0xff0000), delete_after=30)
        elif "error code: 50001" in str(error):
            return await ctx.send(embed=Embed(description="**I don't have access to do this**", color=0xff0000), delete_after=30)
        elif "error code: 30005" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of guild roles reached (250)", color=0xff0000))
        elif "error code: 30007" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of webhooks reached (15)", color=0xff0000))
        elif "error code: 30008" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of emojis reached", color=0xff0000))
        elif "error code: 30010" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of reactions reached (20)", color=0xff0000))
        elif "error code: 30013" in str(error):
            return await ctx.send(embed=Embed(description="Maximum number of guild channels reached (500)", color=0xff0000))
        elif isinstance(error, config.discord.HTTPException):
            await erl.send(f"```json\n{error.text}\nStatus Code : {error.status}\n```")
        else: await erl.send(f"<@885193210455011369>\n```py\nCommand : {ctx.command.name}\nGuild Name: {ctx.guild}\nGuild Id : {ctx.guild.id}\nChannel Id : {ctx.channel.id}\nUser Tag : {ctx.author}\nUser Id : {ctx.author.id}\n\n\n{error}\nTraceback: {traceback.format_exception(error)}\n```")

    except Exception:pass
        #e = str(error)
        #await ctx.reply("Something Went Wrong. Don't worry! I've Reported To Developers. You'll Get Reply Soon.\nThanks For Playing With Me ❤️", delete_after=30)

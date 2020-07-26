import discord
import time
from discord.ext import commands
import asyncio
from discord.ext.commands import Bot
from discord.utils import get
import requests
import datetime
import sqlite3
import random as r
import json
from random import randint


# ПРЕФИКС БОТА
client = commands.Bot(command_prefix="!")
client.remove_command("help")

# ТОКЕН БОТА
token = " "


# СПИСОК ЗАПРЕЩЕННЫХ СЛОВ
bannedwords = ['fuck', 'cunt', 'faggot', 'asshole']

# ПЕРЕМЕННЫЕ ДЛЯ РАБОТЫ С БД
connection = sqlite3.connect("server.db")
cursor = connection.cursor()

# Информация бота
@client.event
async def on_ready():
    print('TEST-BOT-TEST connected')
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Watching"))
    channel = client.get_channel(730744118317285415) #СЮДА АЙДИ ЧАТА КОТОРЫЙ НУЖНО ЧИСТИТЬ КАЖДЫЕ 2 ЧАСА
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        cash BIGINT,
        rep INT,
        exp BIGINT,
        lvl BIGINT
    )""")
    connection.commit()

    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, 1)")
                connection.commit()
            else:
                pass
    connection.commit()
    while True:
        await asyncio.sleep(60)
        await channel.purge(limit=10000)
        dt = datetime.datetime.now()
        value = datetime.datetime.fromtimestamp(time.mktime(dt.timetuple()))
        await channel.send(embed = discord.Embed(title=f":radioactive: Total annihilation! :radioactive:", colour=discord.Color.green(), description=f"{value.strftime('%Y-%m-%d %H:%M:%S')}"))

# Для новых юзеров
@client.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, 1)")
        connection.commit()
    else:
        pass
    role = discord.utils.get(member.guild.roles,id = 731190121558310963) #СЮДА АЙДИ РОЛИ, КОТОРАЯ ВЫДАЕТСЯ ПРИ ЗАХОДЕ НА СЕРВЕР
    await member.add_roles(role)
    await member.send(embed = discord.Embed(description=f"Hello! You have joined Lifty Shifty crew discord server and you were given ‘Guest’ role."
                                                        f" Make sure to visit and read ‘welcome’ channel."
                                                        f" Follow the link to get info about this server and get registered user role."
                                                        f" \n\nhttps://discord.gg/tCTQwpD", colour=discord.Color.green()))

#ФИЛЬТР ЕСЛИ СООБЩЕНИЕ ОТРЕДАКТИРОВАЛИ НА ЗАПРЕЩЕННОЕ
@client.event
async def on_message_edit(before,after):
    await client.process_commands(after)
    mes = after.content.lower()

    for i in bannedwords:
        if i in mes:
            await after.delete()
            msg = await after.channel.send(f'{after.author.mention} Your message has been deleted. Reason: Prohibited Word')
            await asyncio.sleep(3)
            await msg.delete()
            channel = client.get_channel(730744118317285415) # Сюда айди канала в который будут приходить уведомления о нарушении
            emb = discord.Embed(title = 'Violation noticed (editing):', colour = discord.Color.red())
            emb.add_field(name = 'Name:', value = f'{after.author.name}', inline=False)
            emb.add_field(name = 'Reason:', value = f'Banned Word ({mes})')
            emb.set_author(name = client.user.name, icon_url = client.user.avatar_url)

            await channel.send(embed = emb)


#СОЗДАНИЕ ПРИВАТНОЙ РУМЫ
@client.event
async def on_voice_state_update(member,before,after):
    if after.channel.id == 731228561360420884:
        for guild in client.guilds:
            if guild.id == 712160924038856718:
                mainCategory = discord.utils.get(guild.categories, id=731228299409227826)
                channel2 = await guild.create_voice_channel(name=f"{member.display_name}",category=mainCategory)
                await member.move_to(channel2)
                await channel2.set_permissions(member,manage_channels=True)
                def check(a,b,c):
                    return len(channel2.members) == 0
                await client.wait_for('voice_state_update', check=check)
                await channel2.delete()






#ФИЛЬТР и ПОЛУЧЕНИЕ СООБЩЕНИЯ

@client.event
async def on_message(message):
    await client.process_commands(message)
    msg = message.content.lower()
    for i in bannedwords:
        if i in msg:
            rep = int(
                f"""{cursor.execute("SELECT rep FROM users WHERE id = {}".format(message.author.id)).fetchone()[0]}""")
            if rep >= 3:
                await message.delete()
                await message.author.send(embed=discord.Embed(title=f"Your chat has been blocked for frequent abusive language.",
                                                              colour=discord.Color.red()))
                await message.channel.send(f":face_with_symbols_over_mouth:")
                amountt = rep - 1
                cursor.execute("UPDATE users SET rep = rep - {} WHERE id = {}".format(amountt, message.author.id))
                connection.commit()
                role = discord.utils.get(message.author.guild.roles, id=730880586872389813)
                await message.author.add_roles(role)


            else:
                amount = 1
                cursor.execute("UPDATE users SET rep = rep + {} WHERE id = {}".format(amount, message.author.id))
                connection.commit()
                await message.delete()
                await message.author.send(embed=discord.Embed(title=f"Do not swear! Or you will be muted!"
                                                                    f"\n\n                    Warns: **{rep}/3**", colour=discord.Color.dark_gold()))
                await message.channel.send(f":face_with_symbols_over_mouth:")

    amount = r.randint(1,100)
    cursor.execute("UPDATE users SET exp = exp + {} WHERE id = {}".format(amount, message.author.id))
    connection.commit()

    print("----------------------\nСообщение:",msg,
          "\nОт:", message.author,
          "\nCервер:", message.guild,
          "\nИз чата:", message.channel,
          "\n----------------------")

# Тесты(если понадобится)
@client.command(aliases = ["тест"])
@commands.has_permissions(administrator = True)
async def test(ctx):
    await ctx.send(embed=discord.Embed(
        description=f"Hello! You have joined Lifty Shifty crew discord server and you were given ‘Guest’ role."
                    f" Make sure to visit and read ‘welcome’ channel."
                    f" Follow the link to get info about this server and get registered user role."
                    f" \n\nhttps://discord.gg/tCTQwpD", colour=discord.Color.green()))

# Система изменения статуса
@client.command(aliases = ["st"])
@commands.has_permissions(administrator = True)
async def status(ctx, *, msg : str):
    await ctx.channel.purge(limit=1)
    await ctx.send(f"`New Status - {msg}.`")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f"{msg}"))

# Cистема репортов
@client.command(aliases = ["r"])
async def report(ctx, member:discord.Member, *, msg : str):
    await ctx.channel.purge(limit=1)
    # Уведомление пользователя
    embb = discord.Embed(title="Successful.", description="Administration has been awared.", colour=discord.Color.green())
    embb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    embb.set_thumbnail(url="https://avatarko.ru/img/kartinka/5/chelovechek_4170.jpg")
    await ctx.send(embed=embb)
    # Уведомление администрации
    channel = client.get_channel(730744118317285415) # СЮДА АЙДИ КАНАЛА В КОТОРЫЙ БУДЕТ ПРИХОДИТЬ УВЕДОМЛЕНИЕ ДЛЯ АДМИНОВ
    embbe = discord.Embed(title="Report.", description=f"Report on {member.mention} for: `{msg}`",
                         colour=discord.Color.dark_blue())
    embbe.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embbe.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    embbe.set_thumbnail(url="https://image.flaticon.com/icons/png/512/104/104710.png")
    await channel.send(embed=embbe)

    #Уведомление пользователю, которого зарепортили
    emb = discord.Embed(title="You have been reported. Administration has been awared.", description=f"Reason: `{msg}`", colour=discord.Color.red())
    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    emb.set_thumbnail(url="https://pngimg.com/uploads/exclamation_mark/exclamation_mark_PNG64.png")
    await member.send(embed=emb)

# Система создания постов
@client.command(aliases = ["pp"])
@commands.has_permissions(administrator = True)
async def postpic(ctx, urll, *, msg : str = None):
    await ctx.channel.purge(limit=1)
    channel = client.get_channel(730772395446763562) # СЮДА АЙДИ КАНАЛА В КОТОРЫЙ НУЖНО ВЫКЛАДЫВАТЬ ПОСТЫ
    embbe = discord.Embed(title="New post!", description=f"{msg}",
                          colour=discord.Color.blue())
    embbe.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embbe.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    embbe.set_image(url=f"{urll}")
    message = await channel.send("@everyone",embed=embbe)
    await message.add_reaction('👍')
    await message.add_reaction('👎')

@client.command(aliases = ["pv"])
@commands.has_permissions(administrator = True)
async def postvid(ctx, urll, *, msg : str = None):
    await ctx.channel.purge(limit=1)
    channel = client.get_channel(730772395446763562) # СЮДА АЙДИ КАНАЛА В КОТОРЫЙ НУЖНО ВЫКЛАДЫВАТЬ ПОСТЫ
    message = await channel.send(f"@everyone \n**Comment: {msg}** \n{urll}",)
    await message.add_reaction('👍')
    await message.add_reaction('👎')

# Карточка пользователя
@client.command(aliases=['myrole', 'userinfo', 'user'])
async def __userinfo(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    roles = member.roles
    role_list = ""
    for role in roles:
        role_list += f"<@&{role.id}> "
    emb = discord.Embed(title=f'Info about: {member}', colour = 0x179c87)
    emb.set_thumbnail(url=member.avatar_url)
    emb.add_field(name='ID', value=member.id)
    emb.add_field(name='Name', value=member.name)
    emb.add_field(name='Top role:', value=member.top_role)
    emb.add_field(name='Discord ID:', value=member.discriminator)
    emb.add_field(name='Came to our server:', value=member.joined_at.strftime('%Y.%m.%d \n %H:%M:%S'))
    emb.add_field(name='Account Created:', value=member.created_at.strftime("%Y.%m.%d %H:%M:%S"))
    emb.add_field(name='Roles', value=role_list)
    emb.set_footer(text='Called a command: {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)
    await ctx.send(embed = emb)

# Система поздравления
@client.command(aliases = ["dr"])
@commands.has_permissions(administrator = True)
async def happy(ctx, member:discord.Member):
    await ctx.channel.purge(limit=1)

    # Поздравляем пользователя и отправляем это в нужный нам чат.
    channel = client.get_channel(730744118317285415) # СЮДА АЙДИ КАНАЛА В КОТОРЫЙ ПРИДЕТ ПОЗДРАВЛЕНИЕ
    emb = discord.Embed(title="Our server wishes you a Happy Birthday!!!", description=f"{member.mention}", colour=discord.Color.purple())
    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    emb.set_footer(text=f"From {ctx.author.name} for {member.display_name}", icon_url=ctx.author.avatar_url)
    emb.set_thumbnail(url="https://avatanplus.com/files/resources/original/5738aad98306c154b55b61c1.png")
    await channel.send(embed=emb)

#Информация по телефону
@client.command()
@commands.has_permissions( administrator = True)
async def phone_info( ctx, arg = None):
    await ctx.channel.purge(limit=1)
    response = requests.get( f'https://htmlweb.ru/geo/api.php?json&telcod={ arg }' )

    user_country = response.json()[ 'country' ][ 'english' ]
    user_id = response.json()[ 'country' ][ 'id' ]
    user_location = response.json()[ 'country' ][ 'location' ]
    user_city = response.json()[ 'capital' ][ 'english' ]
    user_width = response.json()[ 'capital' ][ 'latitude' ]
    user_lenth = response.json()[ 'capital' ][ 'longitude' ]
    user_post = response.json()[ 'capital' ][ 'post' ]
    user_oper = response.json()[ '0' ][ 'oper' ]

    global all_info
    all_info = f'''**:iphone: Info about phone number {arg}**
    **Operator:** { user_oper }
    **Country:** {user_country}
    **Location:** { user_location }
    **City:** { user_city }
    **Horizontal:** { user_width }
    **Vertical:** { user_lenth }
    **Postcode:** { user_post }
    **ID:** { user_id }'''

    await ctx.send(all_info)

#Информация по айпи
@client.command()
@commands.has_permissions(administrator = True)
async def ip_info( ctx, arg ):
    await ctx.channel.purge(limit=1)
    response = requests.get( f'http://ipinfo.io/{ arg }/json' )

    user_ip = response.json()[ 'ip' ]
    user_city = response.json()[ 'city' ]
    user_region = response.json()[ 'region' ]
    user_country = response.json()[ 'country' ]
    user_location = response.json()[ 'loc' ]
    user_org = response.json()[ 'org' ]
    user_timezone = response.json()[ 'timezone' ]

    global all_info
    emb = discord.Embed(title = f'Info about IP: {arg}:',
    description = f':united_nations: **Country**: { user_country }\n\n:regional_indicator_r: **Region**: { user_region }\n\n:cityscape: **City**: { user_city }\n\n:map: **Location**: { user_location }\n\n:bust_in_silhouette: **Provider**: { user_org }\n\n:clock: **Time zone**: { user_timezone }', colour= 0x39d0d6, inline = False)
    emb.set_footer(text= "Caused by: {}".format(ctx.message.author), icon_url= ctx.message.author.avatar_url)

    await ctx.send(embed = emb)

#Калькулятор ВКЛЮЧИТЬ ЕСЛИ НУЖНО
#@client.command(aliases = ['count', 'calc', 'вычисли', 'math'])
#async def __count(ctx, *, args = None):
#    await ctx.channel.purge(limit=1)
#    text = ctx.message.content
#
#    if args == None:
#        await ctx.send(embed = discord.Embed(description = 'Please, specify expression to evaluate.', color = 0x39d0d6))
#    else:
#        result = eval(args)
#        await ctx.send(embed = discord.Embed(Title = f'Evaluation result of:`',description=f"Answer: **{result}**" , color = 0x39d0d6))

#Информация о сервере
@client.command()
async def serverinfo(ctx):
    await ctx.channel.purge(limit=1)
    members = ctx.guild.members
    online = len(list(filter(lambda x: x.status == discord.Status.online, members)))
    offline = len(list(filter(lambda x: x.status == discord.Status.offline, members)))
    idle = len(list(filter(lambda x: x.status == discord.Status.idle, members)))
    dnd = len(list(filter(lambda x: x.status == discord.Status.dnd, members)))
    allchannels = len(ctx.guild.channels)
    allvoice = len(ctx.guild.voice_channels)
    alltext = len(ctx.guild.text_channels)
    allroles = len(ctx.guild.roles)
    embed = discord.Embed(title=f"{ctx.guild.name}", color=0xff0000, timestamp=ctx.message.created_at)
    embed.description=(
        f":timer: Server created: **{ctx.guild.created_at.strftime('%A, %b %#d %Y')}**\n\n"
        f":flag_white: Region: **{ctx.guild.region}\n\nServer Owner: **{ctx.guild.owner}**\n\n"
        f":tools: Bots on server: **{len([m for m in members if m.bot])}**\n\n"
        f":green_circle: Online: **{online}**\n\n"
        f":black_circle: Offline: **{offline}**\n\n"
        f":yellow_circle: AFK: **{idle}**\n\n"
        f":red_circle: Do not disturb: **{dnd}**\n\n"
        f":shield: Verification level: **{ctx.guild.verification_level}**\n\n"
        f":musical_keyboard: Total channels: **{allchannels}**\n\n"
        f":loud_sound: Voice channels: **{allvoice}**\n\n"
        f":keyboard: Text channels: **{alltext}**\n\n"
        f":briefcase: Total roles: **{allroles}**\n\n"
        f":slight_smile: People on the server: **{ctx.guild.member_count}\n\n"
    )

    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.set_footer(text=f"ID: {ctx.guild.id}")
    embed.set_footer(text=f"ID User: {ctx.author.id}")
    await ctx.send(embed=embed)

# Помощь
@client.command(aliases = ["info"])
async def help(ctx):
    await ctx.channel.purge(limit=1)
    # Оформление
    emb = discord.Embed(title="Menu of commands", colour=discord.Color.blue(), description=f'**!serverinfo** - info about server')
    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    emb.set_thumbnail(url="https://www.palitra-system.ru/upload/medialibrary/542/542811db8bdbf4aebd740794e3380d89.png")
    # Список команд
    emb.add_field(name = "`!help`|`!info`", value="Server menu")
    emb.add_field(name="`!report`|`!r`", value="Send report")
    emb.add_field(name=f"`!user`|`!myrole`", value="Member card")
    emb.add_field(name=f"`!lvl`|`!rank`", value="Member experience")
    emb.add_field(name=f"`!ahelp`|`!adm`", value="Help for administration")
    # Отправка
    await ctx.send(embed=emb)

@client.command(aliases = ["adm"])
@commands.has_permissions(administrator = True)
async def ahelp(ctx):
    await ctx.channel.purge(limit=1)
    # Оформление
    emb = discord.Embed(title="Menu of admin commands", colour=discord.Color.dark_red(), description=f'**!ip_info** - info about ip'
                                                                                                     f'\n**!phone_info** - info about phone')
    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    emb.set_thumbnail(url="https://www.palitra-system.ru/upload/medialibrary/542/542811db8bdbf4aebd740794e3380d89.png")
    # Список команд
    emb.add_field(name = "`!clear`", value="Clear chat")
    emb.add_field(name="`!pv`|`!postvid`", value="Create video post")
    emb.add_field(name=f"`!pp`|`!postpic`", value="Create picture post")
    emb.add_field(name=f"`!ban`|`!kick`", value="Ban and Kick")
    emb.add_field(name=f"`!mute`|`!unmute`", value="Mute and Unmute")
    emb.add_field(name=f"`!unban`", value="Unban banned peoples")
    emb.add_field(name=f"`!st`|`!status`", value="Change BOT status")
    emb.add_field(name=f"`!addxp`|`!addlvl`", value="Add stats")
    emb.add_field(name=f"`!takexp`|`!takel`", value="Del stats")
    emb.add_field(name=f"`!dr`|`!happy`", value="Member Congratulations")
    emb.add_field(name=f"`!rs`|`!rsup`", value="Info about RockStar servers")
    # Отправка
    await ctx.send(embed=emb)

#МУТ И РАЗМУТ
@client.command()
@commands.has_permissions(administrator = True)
async def mute(ctx,member:discord.Member):
    await ctx.channel.purge(limit=1)
    mute_role = discord.utils.get(ctx.message.guild.roles, name = "mute")
    await member.add_roles(mute_role)
    channel = client.get_channel(730744118317285415) # СЮДА АЙДИ КАНАЛА В КОТОРЫЙ ПРИДЕТ УВЕДОМЛЕНИЕ ДЛЯ АДМИНИСТРАЦИИ
    embbe = discord.Embed(title="MUTE", description=f"{member.mention} was muted!",
                          colour=discord.Color.red())
    embbe.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embbe.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    embbe.set_thumbnail(url="https://cdn4.iconfinder.com/data/icons/complete-common-version-6-4/1024/volume_off-512.png")
    await channel.send(embed=embbe)

@client.command()
@commands.has_permissions(administrator = True)
async def unmute(ctx,member:discord.Member):
    await ctx.channel.purge(limit=1)
    mute_role = discord.utils.get(ctx.message.guild.roles, name = "mute")
    await member.remove_roles(mute_role)
    channel = client.get_channel(730744118317285415) # СЮДА АЙДИ КАНАЛА В КОТОРЫЙ ПРИДЕТ УВЕДОМЛЕНИЕ ДЛЯ АДМИНИСТРАЦИИ
    embbe = discord.Embed(title="MUTE", description=f"{member.mention} was unmuted!",
                          colour=discord.Color.green())
    embbe.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embbe.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    embbe.set_thumbnail(url="https://cdn.iconscout.com/icon/free/png-512/unmute-433180.png")
    await channel.send(embed=embbe)

# КИК
@client.command()
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge(limit = 1)
    await member.kick(reason = reason)

# БАН
@client.command()
@commands.has_permissions(administrator = True)
async def ban(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge(limit=1)
    await member.ban(reason=reason)

# РАЗБАН
@client.command(aliases = ["ub"])
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    await ctx.channel.purge(limit=1)
    bannned_users = await ctx.guild.bans()
    for ban_entry in bannned_users:
        user = ban_entry.user
        await ctx.guild.unban(user)
        return

# Очистка чата
@client.command()
@commands.has_permissions(administrator = True)
async def clear(ctx):
    amount = 100
    await ctx.channel.purge(limit=amount)
    await asyncio.sleep(1)
    await ctx.send(":infinity: `Chat was successfully cleared` :infinity:")
    await asyncio.sleep(1)
    await ctx.channel.purge(limit=2)
    print("Чат очищен")

# Система уровней
@client.command(aliases=["exp", "rank", "myrank", "lvl"])
async def __balance(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(title="Error!",
            description=f"Please be sure to specify the user.",
            colour=discord.Color.dark_gold()
        ))
    else:
        exp = int(f"""{cursor.execute("SELECT exp FROM users WHERE id = {}".format(member.id)).fetchone()[0]}""")
        lvl = int(f"""{cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}""")
        if exp >= 20000:
            amount = exp
            cursor.execute("UPDATE users SET exp = exp - {} WHERE id = {}".format(amount, member.id))
            connection.commit()
            amountt = exp // 20000
            cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(amountt, member.id))
            connection.commit()
        exp = int(f"""{cursor.execute("SELECT exp FROM users WHERE id = {}".format(member.id)).fetchone()[0]}""")
        lvl = int(f"""{cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}""")
        await ctx.send(embed=discord.Embed(title=f"Stats of: {member.display_name}",
            description=f"""**LVL** is **{lvl}** :gem:\n**EXP** is **{exp}/20000** :infinity: """,
            colour=discord.Color.magenta()
        ))

@client.command(aliases=["addexp", 'expadd', 'addxp', 'xpadd'])
@commands.has_permissions(administrator = True)
async def __addexp(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, specify user")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, indicate quantity")
        elif amount < 1:
            await ctx.send(f"**{ctx.author}**, indicate quantity greater than 1")
        else:
            cursor.execute("UPDATE users SET exp = exp + {} WHERE id = {}".format(amount, member.id))
            connection.commit()
            await ctx.message.add_reaction('💚')

@client.command(aliases=["remexp", 'exprem', 'remxp', 'takexp'])
@commands.has_permissions(administrator = True)
async def __delexp(ctx, member: discord.Member = None, amount: int = None):
    exp = int(f"""{cursor.execute("SELECT exp FROM users WHERE id = {}".format(member.id)).fetchone()[0]}""")
    if member is None:
        await ctx.send(f"**{ctx.author}**, specify user")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, indicate quantity")
        elif amount < 1:
            await ctx.send(f"**{ctx.author}**, indicate quantity greater than 1")
        elif amount > exp:
            await ctx.send(f"**{ctx.author}**, you can`t do this")
        else:
            cursor.execute("UPDATE users SET exp = exp - {} WHERE id = {}".format(amount, member.id))
            connection.commit()
            await ctx.message.add_reaction('💔')

@client.command(aliases=["addlvl", 'lvladd', 'addl', 'ladd'])
@commands.has_permissions(administrator = True)
async def __addlvl(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, specify user")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, indicate quantity")
        elif amount < 1:
            await ctx.send(f"**{ctx.author}**, indicate quantity greater than 1")
        else:
            cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(amount, member.id))
            connection.commit()
            await ctx.message.add_reaction('💚')

@client.command(aliases=["remlvl", 'lvlrem', 'reml', 'takel'])
@commands.has_permissions(administrator = True)
async def __remlvl(ctx, member: discord.Member = None, amount: int = None):
    lvl = int(f"""{cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}""")
    if member is None:
        await ctx.send(f"**{ctx.author}**, specify user")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, indicate quantity greater than 1")
        elif amount < 1:
             await ctx.send(f"**{ctx.author}**, indicate quantity greater than 1")
        elif amount > lvl:
            await ctx.send(f"**{ctx.author}**, you can`t do this")
        else:
            cursor.execute("UPDATE users SET lvl = lvl - {} WHERE id = {}".format(amount, member.id))
            connection.commit()
            await ctx.message.add_reaction('💔')




# СИСТЕМА ОТСЛЕЖИВАГИЯ СЕРВЕРОВ РОКСТАР!!!!!!!!!!!!!!!

#ОБНОВЛЕНИЕ ДОКУМЕНТА
@client.command(aliases=["rsup"])
@commands.has_permissions(administrator = True)
async def rockstartupdate(ctx):
    await ctx.channel.purge(limit=1)
    request = requests.get("https://support.rockstargames.com/services/status.json?tz=Europe/Moscow")
    request_text = request.text

    data = json.loads(request_text)
    data_serialized = json.dump(data, open('data.json', 'w'), indent=4)

#ПРОСМОТР СТАТИСТИКИ
@client.command(aliases=["rstatus"])
@commands.has_permissions(administrator = True)
async def rs(ctx):
    await ctx.channel.purge(limit=1)
    filename = "data.json"
    myfile = open(filename, mode='r', encoding='Latin-1')
    json_data = json.load(myfile)
    print(json_data)
    comp = []
    comp2 = []
    for i in json_data['services']:
        name = i['name']
        status = i['status_tag']
        comp.append(name)
        comp2.append(status)
    if comp2[0] == 'Up':
        comp2[0] = '💚'
    elif comp2[0] == 'Limited':
        comp2[0] = '💛'
    else:
        comp2[0] = '💔'

    if comp2[1] == 'Up':
        comp2[1] = '💚'
    elif comp2[1] == 'Limited':
        comp2[1] = '💛'
    else:
        comp2[1] = '💔'

    if comp2[2] == 'Up':
        comp2[2] = '💚'
    elif comp2[2] == 'Limited':
        comp2[2] = '💛'
    else:
        comp2[2] = '💔'

    if comp2[3] == 'Up':
        comp2[3] = '💚'
    elif comp2[3] == 'Limited':
        comp2[3] = '💛'
    else:
        comp2[3] = '💔'

    if comp2[4] == 'Up':
        comp2[4] = '💚'
    elif comp2[4] == 'Limited':
        comp2[4] = '💛'
    else:
        comp2[4] = '💔'

    if comp2[5] == 'Up':
        comp2[5] = '💚'
    elif comp2[5] == 'Limited':
        comp2[5] = '💛'
    else:
        comp2[5] = '💔'

    embbe = discord.Embed(title=f"🌌  Rockstart Service Status  🌌",description=f"\n**💚  Up | 💛  Limited | 💔  Down**"
                                                                                f"\n\n\n**🐴 {comp[1]}** - {comp2[1]}"
                                                             f"\n\n**🚓 {comp[2]}** - {comp2[2]}"
                                                             f"\n\n**💬 {comp[3]}** - {comp2[3]}"
                                                             f"\n\n**🚀 {comp[5]}** - {comp2[5]}", url="https://support.rockstargames.com/servicestatus", colour=discord.Color.gold())
    embbe.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embbe.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    embbe.set_thumbnail(url="https://img.icons8.com/all/500/rockstar-games.png")
    await ctx.channel.send(embed=embbe)





#ОШИБКИ --------------------------------------------------------------------------------------------------
#ОШИБКИ --------------------------------------------------------------------------------------------------
#ОШИБКИ --------------------------------------------------------------------------------------------------
@unmute.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user.")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@mute.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user.")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@__userinfo.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user. `!user <member>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@ahelp.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!pv <url> <description>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@__addexp.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!pv <url> <description>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@__addlvl.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!pv <url> <description>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@__delexp.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!pv <url> <description>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@__remlvl.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!pv <url> <description>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@status.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to indicate the status you want to set. `!status <status>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@report.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!report <member> <reason>`")
    else:
        await ctx.send(f"{ctx.author.mention}, such user does not exist.")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@happy.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user. `!happy <member>`")
    else:
        await ctx.send(f"{ctx.author.mention}, such user does not exist.")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@ban.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user. `!ban <member>`")
    else:
        await ctx.send(f"{ctx.author.mention}, such user does not exist.")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@kick.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user. `!kick <member>`")
    else:
        await ctx.send(f"{ctx.author.mention}, such user does not exist.")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@unban.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user. `!unban <member>`")
    else:
        await ctx.send(f"{ctx.author.mention}, such user does not exist.")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@clear.error
async def clear_error(ctx,error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@postpic.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!pp <url> <description>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@postvid.error
async def clear_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention}, be sure to specify the user and reason. `!pv <url> <description>`")
    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, you do not have access.")
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound ):
        await ctx.send(embed = discord.Embed(description = f'**:exclamation: {ctx.author.name}, this command does not exist.**', color=0x0c0c0c))


# ЗАПУСКАЕМ БОТА
client.run(token)

# bot.py
import os
from random import randint
from time import sleep

import discord
from dotenv import load_dotenv

# kk - Generally this code is good, if over-commented (I can generally tell what a foreach loop does and what an
# if or else condition means). It uses some neat Python tricks I didn't know, and is pretty succinct. My notes are mainly
# about style, convention, and organization, but I've given you some performance optimizations to consider as well.

exemption_names = ['Tsuvarskyei', 'LunaVolpe']
exemption_members = []
admin_names = ['Tsuvarskyei', 'katie', 'Haley', 'Pockets', 'pixel_person']
custom_match_names = ['Starkitty23', 'nanji', 'Chelskiee', 'Phasma', 'Mari', 'KittyKabobs', 'Ava_tf', 'Miska']
custom_match_members = []
channel_list = ['tsu-the-bot']
list_of_giveaways = {'serverbooster': ['Server Boosters', 'server booster'], 'custommatch': ['Custom Match'],
                     'ally': ['Allies', 'ally'], 'ashley': ['Ashleys', 'ashley'], 'admin': ['Admins', 'admin']}
list_of_commands = [';;serverbooster', ';;custommatch', ';;ashley', ';;ally', ';;admin']

# kk - I would enclose this in a main() method and call that from a 'if __name__ == "__main__"' block.
# In short, it guards against the possibility that someone does "import Giveaway_Text_2" and accidentally
# launches the bot (say, if you were running unit tests).
# For a more detailed example, see https://stackoverflow.com/questions/419163/what-does-if-name-main-do
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = discord.Client()

# kk - Look into Python docstrings instead of mere comments


async def giveaway(key, message, number):
    list_of_participants = populate_list(key, message)
    list_of_lists = split_lists(list_of_participants)
    await message.channel.send("Drawing for " + list_of_giveaways.get(key)[0] + " from list of eligible participants:")
    for each in list_of_lists:
        await message.channel.send('`' + str([y.display_name for y in each]) + '`')

    if number == 1:
        await message.channel.send("The winner is")
    else:
        await message.channel.send("The winners are")

    for each in range(3):
        sleep(.5)
        await message.channel.send(":drum:")

    for each in range(number):
        winner = list_of_participants[randint(0, len(list_of_participants) - 1)]
        exemption_members.append(winner)
        list_of_participants.remove(winner)
        await message.channel.send(":tada:" + winner.mention + ":tada:")

# kk - I'm curious why this loads a global variable, but split_lists() returns a separate list.
# I think it would make more sense if they both return a list and the global variable was eliminated.


def populate_list(key, message):
    list_of_participants = []
    if key == 'admin':
        for each in message.guild.members:
            # kk - This evaluates the list twice. Can you do it in a single pass over the list?
            if 'admin' in [y.name.lower() for y in each.roles] or '👀' in [y.name.lower() for y in each.roles]:
                if each not in exemption_members:
                    list_of_participants.append(each)

    # kk - So this is essentially a duplicate of the code in the first case. Can this repeated functionality
    # (returning a list of guild members who do/don't have particular roles)
    # be refactored into a function?
    if key == 'custommatch':
        for each in custom_match_members:
            if 'admin' not in [y.name.lower() for y in each.roles]:
                if '👀' not in [y.name.lower() for y in each.roles]:
                    if each not in exemption_members:
                        list_of_participants.append(each)
    else:
        for each in message.guild.members:
            if list_of_giveaways.get(key)[1] in [y.name.lower() for y in each.roles]:
                if 'admin' not in [y.name.lower() for y in each.roles]:
                    if '👀' not in [y.name.lower() for y in each.roles]:
                        if each not in exemption_members:
                            list_of_participants.append(each)
    return list_of_participants

# kk - This iterates over the list several times and allocates more memory than it has to, though it does take advantage
# of a neat trick in Python that I'm impressed by.
# Can you do it in a single pass over the list and only allocate as many lists as you'll eventually return?
# (hint: you'll need to measure the length of each list item's display name, and store an increasing sum in a variable)


# def split_lists(list_of_participants, max_length):
#     list_of_lists = []
#     current_length = 0
#     start_point = 0
#     for each in list_of_participants:
#         current_length += len(each.display_name)
#         if current_length >= max_length:
#             list_of_lists.append(list_of_participants[start_point:each.index()])
#             print("Test Successful")

def split_lists(list_of_items: list, max_length: int = 1500) -> list:
    """Take a list of objects and split it into lists whose str() approach but does not exceed max_length."""
    list_of_lists = []
    current_length = 0
    start_point = 0
    for each in range(len(list_of_items)):
        current_length += len(list_of_items[each]) + 4
        try:
            if current_length + len(list_of_items[each + 1]) + 4 > max_length:
                list_of_lists.append(list_of_items[start_point:each + 1])
                current_length = 0
                start_point = each + 1
        except IndexError:
            pass
    list_of_lists.append(list_of_items[start_point:])
    return list_of_lists

@client.event
async def on_ready():
    # kk - Two things:
    # 1. As written, this code iterates over the entire list of guild members, even after it's
    #   found a match. Can you stop searching the list once a match is found?
    # 2. You spend a lot of time iterating over that list. Can you turn the list into a dictionary
    #   mapping "name -> member object" and use that instead?

    for member in client.guilds[1].members:
        for y in range(len(exemption_names)):
            if member.name == exemption_names[y]:
                exemption_members.append(member)

    for y in range(len(custom_match_names)):
        for member in client.guilds[1].members:
            if member.name == custom_match_names[y]:
                custom_match_members.append(member)
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user or message.channel.name not in channel_list:
        return

    if message.content[:-1] not in list_of_commands and message.content[:-2] not in list_of_commands and message.content not in list_of_commands:
        return

    if message.author.name not in admin_names:
        await message.channel.send('Only admins can initiate giveaways!')
        return

    # kk - I would highly recommend rewriting this with a regular expression instead. Your expression
    # would resemble ";(ashley|ally)(\d{1,2})?" (and you could use it in place of the list of commands
    # for validation as well!)

    try:
        if type(int(message.content[-1])) == int:
            number = int(message.content[-1])
            key = message.content[2:-1]
    except ValueError:
        number = 1
        key = message.content[2:]
    try:
        if type(int(message.content[-2:-1])) == int:
            number = int(message.content[-2:])
            key = message.content[2:-2]
    except ValueError:
        pass
    await giveaway(key, message, number)

if __name__ == "__main__":
    client.run(token)

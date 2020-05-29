#!/usr/bin/env python
# bot.py
import os
import re
from random import randint
from time import sleep
from datetime import datetime

import discord
from dotenv import load_dotenv


class VoiceTimer:
    def __init__(self, voice_state):
        self.active = True if voice_state else False
        self.total_time = 0


list_of_commands = [';;serverbooster', ';;custommatch', ';;ashley', ';;ally', ';;admin']

channel_list = ['tsu-the-bot']
list_of_giveaways = {'serverbooster': ['Server Boosters', 'server booster'], 'custommatch': ['Custom Match'],
                     'ally': ['Allies', 'ally'], 'ashley': ['Ashleys', 'ashley'], 'admin': ['Admins', 'admin']}

dict_of_voice_times = {}
dict_of_members = {}
dict_of_nicknames = {}
exemptions = ['Tsuvarskyei', 'LunaVolpe']
custom_match = ['Starkitty23', 'nanji', 'Chelskiee', 'Phasma', 'Mari', 'KittyKabobs', 'Ava_tf', 'Miska']
admin_names = ['Tsuvarskyei', 'katie', 'Haley', 'Pockets', 'pixel_person']

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = discord.Client()


async def giveaway(key, message, number):
    """This is the primary body of the WoS Giveaway functionality."""
    list_of_participants = populate_list(key)
    list_of_lists = split_lists(list_of_participants)
    await message.channel.send("Drawing for " + list_of_giveaways.get(key)[0] + " from list of eligible participants:")
    for each in list_of_lists:
        await message.channel.send('`' + str([y for y in each]) + '`')

    if number == 1:
        await message.channel.send("The winner is")
    else:
        await message.channel.send("The winners are")

    for each in range(3):
        sleep(.5)
        await message.channel.send(":drum:")

    for each in range(number):
        winner = list_of_participants[randint(0, len(list_of_participants) - 1)]
        exemptions.append(dict_of_nicknames.get(winner))
        list_of_participants.remove(winner)
        await message.channel.send(":tada:" + dict_of_nicknames.get(winner).mention + ":tada:")


def populate_list(key):
    """This populates a list of member display names, with certain exemptions."""
    list_of_participants = []
    if key == 'admin':
        for each in dict_of_members:
            if 'admin' in [y.name.lower() for y in each.roles] or '👀' in [y.name.lower() for y in each.roles]:
                list_of_participants.append(each.display_name)

    if key == 'custommatch':
        for each in custom_match:
            if each not in exemptions:
                list_of_participants.append(each.display_name)

    else:
        for each in dict_of_members:
            if list_of_giveaways.get(key)[1] in [y.name.lower() for y in dict_of_members.get(each).roles]:
                if dict_of_members.get(each) not in exemptions:
                    list_of_participants.append(dict_of_members.get(each).display_name)
    return list_of_participants


def split_lists(list_of_items: list, max_length: int = 1500) -> list:
    """Take a list of objects and split it into lists whose str() approaches but does not exceed max_length."""
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
    """When the bot connects to Discord, it compiles two dictionaries (name-member and nickname-member),
    then translates the [custommatch] and [exemptions] lists from names to member objects,
    then adds all of the admin and moderator staff to the exemptions list."""

    for member in client.guilds[1].members:
        dict_of_members[member.name] = member
        dict_of_nicknames[member.display_name] = member

    for each in custom_match:
        if dict_of_members.get(each) is not None:
            custom_match.append(dict_of_members.get(each))
    custom_match[:] = [y for y in custom_match if type(y) is discord.member.Member]

    for each in exemptions:
        if dict_of_members.get(each) is not None:
            exemptions.append(dict_of_members.get(each))
    exemptions[:] = [y for y in exemptions if type(y) is discord.member.Member]

    for each in dict_of_members:
        if 'admin' in [y.name.lower() for y in dict_of_members.get(each).roles] \
                or '👀' in [y.name.lower() for y in dict_of_members.get(each).roles]:
            if dict_of_members.get(each) not in exemptions:
                exemptions.append(dict_of_members.get(each))

    for each in dict_of_members:
        dict_of_voice_times[each] = VoiceTimer(dict_of_members.get(each).voice)

    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_message(message):
    """"When the bot detects a message, it first verifies that it was sent in an approved channel,
    then it checks for the ;;role syntax and chooses the role immediately following the ;;,
    then it verifies that an admin is initiating the giveaway,
    then it uses the last three digits of the command to generate the number of winners,
    then it passes the message, the role (key) and the digit (number) to the *giveaway* function."""

    if message.author == client.user or message.channel.name not in channel_list:
        return

    key = re.search("^;;(ashley|ally|admin|custommatch|serverbooster)", message.content)
    if not key:
        return
    key = key.group()[2:]

    if message.author.name not in admin_names:
        await message.channel.send('Only admins can initiate giveaways!')
        return

    number = re.search("\d{1,3}$", message.content)
    number = int(number.group()) if number else 1

    await giveaway(key, message, number)


# @client.event
# async def on_voice_state_update(member, before, after):
#     if after.channel:
#         if not before.channel:
#             if len(dict_of_voice_times.get(member.name)) == 0:
#                 dict_of_voice_times.get(member.name).append(datetime.now())
#             else:
#                 dict_of_voice_times.get(member.name)[0] = datetime.now()
#     else:
#         if before.channel:
#             if len(dict_of_voice_times.get(member.name)) == 0:
#                 return
#             elif len(dict_of_voice_times.get(member.name)) == 1:
#                 dict_of_voice_times.get(member.name).append(datetime.now() - dict_of_voice_times.get(member.name)[0])
#                 print(dict_of_voice_times.get(member.name)[1])
#             else:
#                 difference = datetime.now() - dict_of_voice_times.get(member.name)[0]
#                 dict_of_voice_times.get(member.name)[1] = dict_of_voice_times.get(member.name)[1] + difference
#                 print(dict_of_voice_times.get(member.name)[1])


@client.event
async def on_voice_state_update(member, before, after):
    for each in dict_of_members:
        print(dict_of_members.get(each).voice)






if __name__ == "__main__":
    client.run(token)
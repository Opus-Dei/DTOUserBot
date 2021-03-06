# Copyright (C) 2020 TeamDerUntergang.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

""" Olayları yönetmek için UserBot modülü.
 UserBot'un ana bileşenlerinden biri. """

import sys
from asyncio import create_subprocess_shell as asyncsubshell
from asyncio import subprocess as asyncsub
from os import remove
from time import gmtime, strftime
from traceback import format_exc

from telethon import events

from userbot import bot, BOTLOG_CHATID, LOGSPAMMER, SILINEN_PLUGIN


def register(**args):
    """ Yeni bir etkinlik kaydedin. """
    pattern = args.get('pattern', None)
    disable_edited = args.get('disable_edited', False)
    ignore_unsafe = args.get('ignore_unsafe', False)
    unsafe_pattern = r'^[^/!#@\$A-Za-z]'
    groups_only = args.get('groups_only', False)
    trigger_on_fwd = args.get('trigger_on_fwd', False)
    trigger_on_inline = args.get('trigger_on_inline', False)
    disable_errors = args.get('disable_errors', False)

    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = '(?i)' + pattern

    if "disable_edited" in args:
        del args['disable_edited']

    if "ignore_unsafe" in args:
        del args['ignore_unsafe']

    if "groups_only" in args:
        del args['groups_only']

    if "disable_errors" in args:
        del args['disable_errors']

    if "trigger_on_fwd" in args:
        del args['trigger_on_fwd']
      
    if "trigger_on_inline" in args:
        del args['trigger_on_inline']

    if pattern:
        if not ignore_unsafe:
            args['pattern'] = pattern.replace('^.', unsafe_pattern, 1)

    def decorator(func):
        async def wrapper(check):
            if not LOGSPAMMER:
                send_to = check.chat_id
            else:
                send_to = BOTLOG_CHATID

            if not trigger_on_fwd and check.fwd_from:
                return

            if check.via_bot_id and not trigger_on_inline:
                return
             
            if groups_only and not check.is_group:
                await check.respond("`Zəhmət olmasa qrupda yazın.`")
                return

            try:
                await func(check)
                

            except events.StopPropagation:
                raise events.StopPropagation
            except KeyboardInterrupt:
                pass
            except BaseException:


                if not disable_errors:
                    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

                    text = "**USERBOT XƏTA**\n"
                    link = "[DTÖUserBot Dəstək Qrupu](https://t.me/DTOSupport)"
                    text += "İstəyirsizsə, bunu şikayət edə bilərsiz"
                    text += f"- sadəcə bu mesajı bura yönləndirin {link}.\n"
                    text += "Xətadan başqa heçbir şey qeyd olunmur!\n"

                    ftext = "========== XEBERDARLIQ =========="
                    ftext += "\nBu fayl sadece burada yüklendi,"
                    ftext += "\nsadece xeta ve tarix qismink qeyd eledik,"
                    ftext += "\ngizliliyinize hörmet edirik,"
                    ftext += "\nburada her hansı bir gizli veri varsa"
                    ftext += "\nbu xeta şikayetj olmaya biler, kimse verilerinize oğurlayamaz.\n"
                    ftext += "================================\n\n"
                    ftext += "--------USERBOT XETA GUNLUYU--------\n"
                    ftext += "\nTarix: " + date
                    ftext += "\nQrup ID: " + str(check.chat_id)
                    ftext += "\nGönderen istifadecinin ID: " + str(check.sender_id)
                    ftext += "\n\nHadise:\n"
                    ftext += str(check.text)
                    ftext += "\n\nMelumat:\n"
                    ftext += str(format_exc())
                    ftext += "\n\nHata metni:\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "\n\n--------USERBOT XETA GUNLUYU BITISI--------"

                    command = "git log --pretty=format:\"%an: %s\" -10"

                    ftext += "\n\n\nSon 10 commit:\n"

                    process = await asyncsubshell(command,
                                                  stdout=asyncsub.PIPE,
                                                  stderr=asyncsub.PIPE)
                    stdout, stderr = await process.communicate()
                    result = str(stdout.decode().strip()) \
                        + str(stderr.decode().strip())

                    ftext += result

                    file = open("error.log", "w+")
                    file.write(ftext)
                    file.close()

                    if LOGSPAMMER:
                        await check.client.respond("`Pis xəbərim var :( , UserBotun çökdü.\
                        \nXəta günlükləri UserBot günlük qrupunda saxlanır.`")

                    await check.client.send_file(send_to,
                                                 "error.log",
                                                 caption=text)
                    remove("error.log")
            else:
                pass
        if not disable_edited:
            bot.add_event_handler(wrapper, events.MessageEdited(**args))
        bot.add_event_handler(wrapper, events.NewMessage(**args))

        return wrapper

    return decorator

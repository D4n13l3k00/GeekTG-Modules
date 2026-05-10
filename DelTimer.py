# .------.------.------.------.------.------.------.------.------.------.
# |D.--. |4.--. |N.--. |1.--. |3.--. |L.--. |3.--. |K.--. |0.--. |0.--. |
# | :/\: | :/\: | :(): | :/\: | :(): | :/\: | :(): | :/\: | :/\: | :/\: |
# | (__) | :\/: | ()() | (__) | ()() | (__) | ()() | :\/: | :\/: | :\/: |
# | '--'D| '--'4| '--'N| '--'1| '--'3| '--'L| '--'3| '--'K| '--'0| '--'0|
# `------`------`------`------`------`------`------`------`------`------'
#
#                     Copyright 2023 t.me/D4n13l3k00
#           Licensed under the Creative Commons CC BY-NC-ND 4.0
#
#                    Full license text can be found at:
#       https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
#
#                           Human-friendly one:
#            https://creativecommons.org/licenses/by-nc-nd/4.0

# meta developer: @D4n13l3k00


import asyncio
import contextlib
import re

from friendly_telegram import loader, utils  # type: ignore


_INT_RE = re.compile(r"^\d+$")


@loader.tds
class DelTmMod(loader.Module):
    """Delete Timer"""

    strings = {"name": "Delete Timer"}

    @loader.owner
    async def deltmcmd(self, m):
        ".deltm <reply> <секунды> - Удалить сообщение в реплае через N секунд"
        reply = await m.get_reply_message()
        if not reply:
            return await utils.answer(m, "reply to message...")
        arg = utils.get_args_raw(m) or ""
        if not _INT_RE.match(arg):
            return await utils.answer(m, "укажи время в секундах (целое число)")
        with contextlib.suppress(Exception):
            await m.delete()
        await asyncio.sleep(int(arg))
        with contextlib.suppress(Exception):
            await reply.delete()

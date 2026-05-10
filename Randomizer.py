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


import random
import re

from friendly_telegram import loader, utils  # type: ignore


_RANGE_RE = re.compile(r"^(\d+)\s+(\d+)$")
_PREFIX = "<b>[Рандомайзер]</b>\n"


@loader.tds
class RandomizerMod(loader.Module):
    strings = {"name": "Рандомайзер"}

    @loader.owner
    async def rndintcmd(self, m):
        ".rndint <a> <b> - рандомное число из заданного диапазона"
        args = utils.get_args_raw(m) or ""
        match = _RANGE_RE.match(args)
        if not match:
            return await utils.answer(m, f"{_PREFIX}Укажи диапазон чисел!")
        fr, to = int(match.group(1)), int(match.group(2))
        if fr >= to:
            return await utils.answer(m, f"{_PREFIX}Укажи корректный диапазон!")
        await utils.answer(
            m,
            f"{_PREFIX}<b>Режим:</b> Рандомное число из диапазона\n"
            f"<b>Диапазон:</b> <code>{fr}-{to}</code>\n"
            f"<b>Выпало число:</b> <code>{random.randint(fr, to)}</code>",
        )

    @loader.owner
    async def rndelmcmd(self, m):
        ".rndelm <элементы через запятую> - рандомный элемент из списка"
        args = utils.get_args_raw(m)
        if not args:
            return await utils.answer(
                m, f"{_PREFIX}Напиши список элементов через запятую!"
            )
        lst = [i.strip() for i in args.split(",") if i.strip()]
        if not lst:
            return await utils.answer(m, f"{_PREFIX}Пустой список!")
        joined = utils.escape_html(", ".join(lst))
        choice = utils.escape_html(random.choice(lst))
        await utils.answer(
            m,
            f"{_PREFIX}<b>Режим:</b> Рандомный элемент из списка\n"
            f"<b>Список:</b> <code>{joined}</code>\n"
            f"<b>Выпало:</b> <code>{choice}</code>",
        )

    @loader.owner
    async def rndusercmd(self, m):
        ".rnduser - выбор рандомного юзера из чата"
        if not m.chat:
            return await utils.answer(m, f"{_PREFIX}<b>Это не чат</b>")
        users = await m.client.get_participants(m.chat)
        if not users:
            return await utils.answer(m, f"{_PREFIX}В чате нет участников")
        user = random.choice(users)
        name = utils.escape_html(user.first_name or "no name")
        await utils.answer(
            m,
            f"{_PREFIX}<b>Режим:</b> Рандомный юзер из чата\n"
            f'<b>Юзер:</b> <a href="tg://user?id={user.id}">{name}</a> '
            f"| <code>{user.id}</code>",
        )

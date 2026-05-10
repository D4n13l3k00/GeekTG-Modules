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

import httpx

from friendly_telegram import loader, utils  # type: ignore


_API = "https://api.d4n1.ru/tg/leaked/check"


@loader.tds
class CheckerTGMod(loader.Module):
    """CheckerTG"""

    strings = {
        "name": "CheckerTG",
        "check": "<b>[CheckerAPI]</b> Делаем запрос к API...",
        "response": (
            "<b>[CheckerAPI]</b> Ответ API: <code>{}</code>\n"
            "Время выполнения: <code>{}</code>"
        ),
        "noargs": "<b>[CheckerAPI]</b> А кого чекать?",
        "err": "<b>[CheckerAPI]</b> Ошибка: <code>{}</code>",
    }

    async def _call_api(self, m, params: dict) -> None:
        await utils.answer(m, self.strings["check"])
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(_API, params=params)
                r.raise_for_status()
                data = r.json()
        except (httpx.HTTPError, ValueError) as e:
            return await utils.answer(
                m, self.strings["err"].format(utils.escape_html(str(e)))
            )
        await utils.answer(
            m,
            self.strings["response"].format(
                utils.escape_html(str(data.get("data", ""))),
                f"{round(float(data.get('time', 0)), 3)}ms",
            ),
        )

    @loader.owner
    async def checkcmd(self, m):
        """Проверить id на слитый номер. Жуёт <reply> либо <uid>"""
        reply = await m.get_reply_message()
        args = utils.get_args_raw(m)
        if args:
            user = args
        elif reply and reply.sender:
            user = str(reply.sender.id)
        else:
            return await utils.answer(m, self.strings["noargs"])
        await self._call_api(m, {"uid": user})

    @loader.owner
    async def rcheckcmd(self, m):
        """Обратный поиск. Жуёт <phone number> или reply"""
        reply = await m.get_reply_message()
        args = utils.get_args_raw(m)
        if args:
            phone = args
        elif reply and reply.raw_text:
            phone = reply.raw_text
        else:
            return await utils.answer(m, self.strings["noargs"])
        await self._call_api(m, {"r": 1, "uid": phone})

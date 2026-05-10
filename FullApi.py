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


from html import escape

import httpx

from friendly_telegram import loader, utils  # type: ignore


@loader.tds
class FullApiMod(loader.Module):
    """Фулл"""

    strings = {
        "name": "FullApi",
        "err": "🚫 <b>[FullApi]</b> <code>{}</code>",
        "link": '<a href="{}">Подгончик для братков</a>',
    }

    @loader.owner
    async def rndfullcmd(self, m):
        "получить рандомный фулл :)"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get("https://api.d4n1.ru/shit/random_full")
                r.raise_for_status()
                url = r.json()["url"]
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return await utils.answer(m, self.strings["err"].format(escape(str(e))))

        await utils.answer(m, self.strings["link"].format(escape(url)))

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


@loader.tds
class WttrInMod(loader.Module):
    """WttrIn"""

    strings = {
        "name": "WttrIn",
        "result": "<code>{}</code>",
        "err": "🚫 <b>[WttrIn]</b> <code>{}</code>",
    }

    @loader.owner
    async def wthrcmd(self, m):
        """.wthr <Город если надо>
        Получить текущую погоду
        """
        city = utils.get_args_raw(m) or ""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    f"https://wttr.in/{city}?0Tq&lang=ru",
                    headers={"User-Agent": "curl/8"},
                )
                r.raise_for_status()
                body = r.text
        except httpx.HTTPError as e:
            return await utils.answer(
                m, self.strings["err"].format(utils.escape_html(str(e)))
            )
        await utils.answer(m, self.strings["result"].format(utils.escape_html(body)))

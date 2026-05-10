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


_TYPES = [
    "femdom", "tickle", "classic", "ngif", "erofeet", "meow", "erok", "poke",
    "les", "hololewd", "lewdk", "keta", "feetg", "nsfw_neko_gif", "eroyuri",
    "kiss", "_8ball", "kuni", "tits", "pussy_jpg", "cum_jpg", "pussy",
    "lewdkemo", "lizard", "slap", "lewd", "cum", "cuddle", "spank",
    "smallboobs", "goose", "Random_hentai_gif", "avatar", "fox_girl",
    "nsfw_avatar", "hug", "gecg", "boobs", "pat", "feet", "smug", "kemonomimi",
    "solog", "holo", "wallpaper", "bj", "woof", "yuri", "trap", "anal", "baka",
    "blowjob", "holoero", "feed", "neko", "gasm", "hentai", "futanari", "ero",
    "solo", "waifu", "pwankg", "eron", "erokemo",
]


@loader.tds
class nkapimdMod(loader.Module):
    strings = {
        "name": "NekosLife",
        "unknown": "🚫 <b>[NekosLife]</b> Неизвестная категория",
        "fetching": "<b>Mmm...</b>",
        "err": "🚫 <b>[NekosLife]</b> <code>{}</code>",
        "categories": "Доступные категории:\n{}",
    }

    @loader.owner
    async def nkcmd(self, m):
        "Отправить фото/гиф\nПо умолчанию отправляется neko\nМожно указать другую категорию(.nkct)"
        args = utils.get_args_raw(m)
        typ = args if args else "neko"
        if typ not in _TYPES:
            return await utils.answer(m, self.strings["unknown"])

        await utils.answer(m, self.strings["fetching"])
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(f"https://nekos.life/api/v2/img/{typ}")
                r.raise_for_status()
                url = r.json()["url"]
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return await utils.answer(m, self.strings["err"].format(str(e)))

        reply = await m.get_reply_message()
        await m.client.send_file(
            m.to_id, url, reply_to=reply.id if reply else None
        )
        await m.delete()

    async def nkctcmd(self, m):
        "Список категорий"
        body = "\n".join(f"<code>{t}</code>" for t in _TYPES)
        await utils.answer(m, self.strings["categories"].format(body))

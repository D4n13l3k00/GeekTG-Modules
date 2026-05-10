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


from telethon.tl.types import (
    InputMessagesFilterContacts,
    InputMessagesFilterDocument,
    InputMessagesFilterGeo,
    InputMessagesFilterGif,
    InputMessagesFilterMusic,
    InputMessagesFilterPhotos,
    InputMessagesFilterRoundVideo,
    InputMessagesFilterUrl,
    InputMessagesFilterVideo,
    InputMessagesFilterVoice,
)

from friendly_telegram import loader, utils  # type: ignore


# (Russian label, telethon filter or None for "all messages")
_FILTERS = [
    ("Всего сообщений", None),
    ("Фоток", InputMessagesFilterPhotos),
    ("Видосов", InputMessagesFilterVideo),
    ("Попсы", InputMessagesFilterMusic),
    ("Голосовых", InputMessagesFilterVoice),
    ("Кругляшков", InputMessagesFilterRoundVideo),
    ("Файлов", InputMessagesFilterDocument),
    ("Ссылок", InputMessagesFilterUrl),
    ("Гифок", InputMessagesFilterGif),
    ("Координат", InputMessagesFilterGeo),
    ("Контактов", InputMessagesFilterContacts),
]


@loader.tds
class ChatStatisticMod(loader.Module):
    "Статистика чата"
    strings = {"name": "ChatStatistic"}

    @loader.owner
    async def statacmd(self, m):
        "Статистика сообщений в чате"
        await utils.answer(m, "<b>Считаем...</b>")
        lines = []
        for label, flt in _FILTERS:
            kwargs = {"filter": flt()} if flt is not None else {}
            res = await m.client.get_messages(m.to_id, limit=0, **kwargs)
            lines.append(f"<b>{label}:</b> {res.total}")
        await utils.answer(m, "\n".join(lines))

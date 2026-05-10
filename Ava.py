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


import contextlib
import os

from telethon import functions, types

from friendly_telegram import loader, utils  # type: ignore


@loader.tds
class AvaMod(loader.Module):
    """Установка/удаление аватарок через команды"""

    strings = {
        "name": "AvatarMod",
        "need_pic": "<b>[Avatar]</b> Нужно фото",
        "downloading": "<b>[Avatar]</b> Скачиваю",
        "installing": "<b>[Avatar]</b> Устанавливаю",
        "deleting": "<b>[Avatar]</b> Удаляю",
        "ok": "<b>[Avatar]</b> Готово",
        "no_avatar": "<b>[Avatar]</b> Нету аватарки/ок",
    }

    async def _delete_photos(self, m: types.Message, limit) -> None:
        client = m.client
        kwargs = {"limit": limit} if limit is not None else {}
        ava = await client.get_profile_photos("me", **kwargs)
        if not ava:
            return await utils.answer(m, self.strings["no_avatar"])
        progress = await utils.answer(m, self.strings["deleting"])
        await client(functions.photos.DeletePhotosRequest(ava))
        await utils.answer(progress, self.strings["ok"])

    @loader.owner
    async def avacmd(self, m: types.Message):
        ".ava <reply_to_photo> - Установить аватар"
        client = m.client
        reply = await m.get_reply_message()
        if not reply or not reply.photo:
            return await utils.answer(m, self.strings["need_pic"])

        progress = await utils.answer(m, self.strings["downloading"])
        photo = await client.download_media(message=reply.photo)
        try:
            up = await client.upload_file(photo)
            progress = await utils.answer(progress, self.strings["installing"])
            await client(functions.photos.UploadProfilePhotoRequest(up))
            await utils.answer(progress, self.strings["ok"])
        finally:
            with contextlib.suppress(OSError):
                if photo:
                    os.remove(photo)

    @loader.owner
    async def delavacmd(self, m: types.Message):
        "Удалить текущую аватарку"
        await self._delete_photos(m, limit=1)

    @loader.owner
    async def delavascmd(self, m: types.Message):
        "Удалить все аватарки"
        await self._delete_photos(m, limit=None)

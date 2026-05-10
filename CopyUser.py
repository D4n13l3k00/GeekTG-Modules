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

from telethon import functions
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

from friendly_telegram import loader, utils  # type: ignore


@loader.tds
class CuMod(loader.Module):
    """Полное копирование юзера (ава, имя/фамилия, био)"""

    strings = {"name": "CopyUser"}

    async def _progress(self, message, silent: bool, text: str) -> None:
        if silent:
            return
        with contextlib.suppress(Exception):
            await message.edit(text)

    async def _resolve_user(self, message, args, reply):
        for tok in args:
            low = tok.lower()
            if low in ("s", "a", "а"):
                continue
            try:
                return await message.client.get_entity(tok)
            except Exception:
                continue
        return reply.sender if reply else None

    @loader.owner
    async def cucmd(self, message):
        """.cu <s> <a> <reply/@username>
        <s> - Скрытый режим
        <a> - Удалить ваши аватарки
        Примеры: .cu s @user / .cu a reply / .cu s a @user
        """
        reply = await message.get_reply_message()
        raw = utils.get_args_raw(message) or ""
        args = raw.split()
        flags = {a.lower() for a in args}
        silent = "s" in flags
        wipe = "a" in flags or "а" in flags

        user = await self._resolve_user(message, args, reply)
        if user is None:
            if not silent:
                with contextlib.suppress(Exception):
                    await message.edit("Кого?")
            return

        if silent:
            with contextlib.suppress(Exception):
                await message.delete()
        else:
            for i in range(0, 11, 2):
                await self._progress(
                    message,
                    silent,
                    f"Получаем доступ к аккаунту пользователя [{i*10}%]\n"
                    f"[{(i*'#').ljust(10, '–')}]",
                )
                await asyncio.sleep(0.3)

        if wipe:
            avs = await message.client.get_profile_photos("me")
            if avs:
                with contextlib.suppress(Exception):
                    await message.client(
                        functions.photos.DeletePhotosRequest(avs)
                    )

        full = await message.client(GetFullUserRequest(user.id))
        await self._progress(message, silent, "Получаем аватарку... [35%]\n[###–––––––]")
        if full.profile_photo:
            blob = await message.client.download_profile_photo(user, bytes)
            if blob:
                up = await message.client.upload_file(blob)
                await self._progress(
                    message, silent, "Ставим аватарку... [50%]\n[#####–––––]"
                )
                with contextlib.suppress(Exception):
                    await message.client(
                        functions.photos.UploadProfilePhotoRequest(up)
                    )

        await self._progress(message, silent, "Получаем данные...  [99%]\n[#########–]")
        await message.client(
            UpdateProfileRequest(
                user.first_name or "",
                user.last_name or "",
                (full.about or "")[:70],
            )
        )

        if not silent:
            await self._progress(
                message, silent, "Аккаунт клонирован! [100%]\n[##########]"
            )
            await asyncio.sleep(5)
            await self._progress(message, silent, "Аккаунт клонирован!")

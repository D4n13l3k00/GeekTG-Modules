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
import csv
import io

from friendly_telegram import loader, utils  # type: ignore


@loader.tds
class DUsersMod(loader.Module):
    """DUsers"""

    strings = {"name": "DUsers"}

    @loader.owner
    async def ducmd(self, message):
        """.du <n> <m> <s>
        Дамп юзеров чата
        <n> - Только пользователи с открытыми номерами
        <m> - Отправить дамп в избранное
        <s> - Тихий дамп
        """
        if not message.chat:
            return await utils.answer(message, "<b>Это не чат</b>")

        args = (utils.get_args_raw(message) or "").lower()
        only_num = "n" in args
        silent = "s" in args
        tome = "m" in args

        if silent:
            with contextlib.suppress(Exception):
                await message.delete()
        else:
            await utils.answer(message, "🖤Дампим чат...🖤")

        # csv module handles quoting/escaping properly (defends against
        # commas/semicolons/newlines/quotes in user-controlled fields).
        text_buf = io.StringIO()
        writer = csv.writer(text_buf, delimiter=";")
        writer.writerow(["FNAME", "LNAME", "USER", "ID", "NUMBER"])

        me = await message.client.get_me()
        for u in await message.client.get_participants(message.to_id):
            if u.id == me.id:
                continue
            if only_num and not u.phone:
                continue
            writer.writerow(
                [u.first_name or "", u.last_name or "", u.username or "",
                 u.id, u.phone or ""]
            )

        f = io.BytesIO(text_buf.getvalue().encode())
        f.name = f"Dump by {message.chat.id}.csv"

        target = "me" if tome else message.to_id
        await message.client.send_file(
            target, f, caption=f"Дамп чата {message.chat.id}"
        )

        if not silent:
            if tome:
                tail = (
                    "Дамп юзеров чата с открытыми номерами сохранён в избранных!"
                    if only_num
                    else "Дамп юзеров чата сохранён в избранных!"
                )
                await utils.answer(message, f"🖤{tail}🖤")
            else:
                with contextlib.suppress(Exception):
                    await message.delete()

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
import io
import logging
from dataclasses import dataclass
from typing import List, Optional

import httpx
from telethon import types
from telethon.events import ChatAction
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from friendly_telegram import loader, utils

logger = logging.getLogger(__name__)

_CAPTCHA_TIMEOUT = 60


@dataclass
class CUser:
    chat: int
    user: int
    message: int
    answer: str


@loader.tds
class CaptchaMod(loader.Module):
    "Captcha for chats"
    strings = {
        "name": "Captcha",
        "pls_pass_captcha": (
            '<a href="tg://user?id={}">Хэй</a>, пройди капчу! У тебя одна попытка\n'
            "Иначе получишь бан навсегда!"
        ),
        "captcha_status": "<b>[Captcha]</b> {}",
    }

    _table = "CaptchaMod"

    def __init__(self):
        self.locked_users: List[CUser] = []

    # ---------------------------------------------------------------- helpers

    def _pop_locked(self, chat: int, user: int) -> Optional[CUser]:
        for u in self.locked_users:
            if u.chat == chat and u.user == user:
                self.locked_users.remove(u)
                return u
        return None

    async def _ban(self, client, chat: int, user: int) -> None:
        with contextlib.suppress(Exception):
            await client(
                EditBannedRequest(
                    chat,
                    user,
                    ChatBannedRights(until_date=None, view_messages=True),
                )
            )

    async def _delete_msg(self, client, chat: int, msg_id: int) -> None:
        with contextlib.suppress(Exception):
            msg = await client.get_messages(chat, ids=msg_id)
            if msg:
                await msg.delete()

    async def _expire_after(self, client, chat: int, user: int) -> None:
        await asyncio.sleep(_CAPTCHA_TIMEOUT)
        entry = self._pop_locked(chat, user)
        if not entry:
            return
        await self._delete_msg(client, entry.chat, entry.message)
        await self._ban(client, entry.chat, entry.user)

    async def _challenge(self, client, chat_id: int, user_id: int) -> None:
        try:
            async with httpx.AsyncClient(timeout=15) as http:
                r = await http.get("https://api.d4n1.ru/captcha/generate")
                r.raise_for_status()
                answer = r.headers["Captcha-Code"]
                im = io.BytesIO(r.content)
        except (httpx.HTTPError, KeyError) as e:
            logger.warning("captcha fetch failed: %s", e)
            return

        im.name = "@DekFTGModules_captcha.png"
        sent = await client.send_file(
            chat_id,
            im,
            caption=self.strings("pls_pass_captcha").format(user_id),
        )
        self.locked_users.append(
            CUser(chat=sent.chat_id, user=user_id, message=sent.id, answer=answer)
        )
        asyncio.create_task(self._expire_after(client, sent.chat_id, user_id))

    # ---------------------------------------------------------------- watcher

    async def watcher(self, event):
        client = event.client
        if isinstance(event, ChatAction.Event):
            if event.chat_id not in self.ctx.db.get(self._table, "chats", []):
                return
            users = [i.id for i in event.users] if event.users else []
            if event.user_added or event.user_joined:
                for uid in users:
                    try:
                        ent = await client.get_entity(uid)
                    except Exception:
                        continue
                    if getattr(ent, "bot", False):
                        continue
                    await self._challenge(client, event.chat_id, uid)
            elif event.user_kicked or event.user_left:
                for uid in users:
                    self._pop_locked(event.chat_id, uid)
            return

        if isinstance(event, types.Message):
            entry = self._pop_locked(event.chat_id, event.sender_id)
            if not entry:
                return
            await self._delete_msg(client, entry.chat, entry.message)
            with contextlib.suppress(Exception):
                await event.delete()
            if entry.answer.lower() != (event.raw_text or "").lower():
                await self._ban(client, entry.chat, entry.user)

    # --------------------------------------------------------------- commands

    async def swcaptchacmd(self, m: types.Message):
        "Turn on/off captcha in chat"
        chats: list = self.ctx.db.get(self._table, "chats", [])
        if m.chat_id in chats:
            chats.remove(m.chat_id)
            self.ctx.db.set(self._table, "chats", chats)
            return await utils.answer(m, self.strings("captcha_status").format("OFF"))
        chats.append(m.chat_id)
        self.ctx.db.set(self._table, "chats", chats)
        await utils.answer(m, self.strings("captcha_status").format("ON"))

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


# requires: ShazamAPI

import asyncio
import io
import logging
from dataclasses import dataclass
from typing import Optional

from ShazamAPI import Shazam

from friendly_telegram import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class ShazamTrack:
    track: io.BytesIO
    reply: object


_TAG = "<b>[Shazam]</b> "


@loader.tds
class ShazamMod(loader.Module):
    """Shazam API"""

    strings = {
        "name": "Shazam API",
        "downloading": "<b>[Shazam]</b> Скачиваю...",
        "recognizing": "<b>[Shazam]</b> Распознаю...",
        "reply_audio": "<b>[Shazam]</b> reply to audio...",
        "fail": "<b>[Shazam]</b> Не удалось распознать...",
        "fail_text": "<b>[Shazam]</b> Не удалось распознать... | Текста нет...",
        "track_caption": "<b>[Shazam]</b> Распознанный трек: {}",
        "track_text": "<b>[Shazam]</b> Текст трека {}\n\n{}",
    }

    async def _recognize(self, payload: bytes) -> Optional[dict]:
        """Run the blocking Shazam call off the event loop."""

        def _do() -> Optional[dict]:
            recog = Shazam(payload).recognizeSong()
            try:
                return next(recog)[1]["track"]
            except (StopIteration, KeyError, IndexError):
                return None

        try:
            return await asyncio.to_thread(_do)
        except Exception:
            logger.exception("Shazam recognize failed")
            return None

    @loader.owner
    async def shazamcmd(self, m):
        """.shazam <reply to audio> - распознать трек"""
        s = await self._get_audio(m)
        if not s:
            return
        track = await self._recognize(s.track.read())
        if not track:
            return await utils.answer(m, self.strings["fail"])
        try:
            await m.client.send_file(
                m.to_id,
                file=track["images"]["background"],
                caption=self.strings["track_caption"].format(
                    utils.escape_html(track["share"]["subject"])
                ),
                reply_to=s.reply.id,
            )
            await m.delete()
        except (KeyError, Exception) as e:
            logger.warning("shazamcmd send failed: %s", e)
            await utils.answer(m, self.strings["fail"])

    @loader.owner
    async def shazamtextcmd(self, m):
        """.shazamtext <reply to audio> - узнать текст трека"""
        s = await self._get_audio(m)
        if not s:
            return
        track = await self._recognize(s.track.read())
        if not track:
            return await utils.answer(m, self.strings["fail_text"])
        try:
            text = track["sections"][1]["text"]
        except (KeyError, IndexError, TypeError):
            return await utils.answer(m, self.strings["fail_text"])

        body = "\n".join(text) if isinstance(text, list) else str(text)
        await utils.answer(
            m,
            self.strings["track_text"].format(
                utils.escape_html(track["share"]["subject"]),
                utils.escape_html(body),
            ),
        )

    async def _get_audio(self, m) -> Optional[ShazamTrack]:
        reply = await m.get_reply_message()
        if not (
            reply
            and reply.file
            and reply.file.mime_type
            and reply.file.mime_type.split("/", 1)[0] == "audio"
        ):
            await utils.answer(m, self.strings["reply_audio"])
            return None

        await utils.answer(m, self.strings["downloading"])
        track = io.BytesIO(await reply.download_media(bytes))
        await utils.answer(m, self.strings["recognizing"])
        return ShazamTrack(track=track, reply=reply)

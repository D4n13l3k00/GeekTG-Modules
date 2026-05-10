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
import os
import random
import string

from friendly_telegram import loader, utils  # type: ignore


_LEVELS = {
    "1": "1M",
    "2": "0.5M",
    "3": "0.1M",
    "4": "0.05M",
    "5": "0.01M",
}


def _rand_filename() -> str:
    return "".join(random.choice(string.ascii_letters) for _ in range(25)) + ".mp4"


@loader.tds
class VSHAKALMod(loader.Module):
    strings = {"name": "Video Shakal"}

    @loader.owner
    async def vshcmd(self, m):
        ".vsh <реплай на видео> <уровень 1-5 (по умолч. 3)> - Сшакалить видео"
        reply = await m.get_reply_message()
        if not (
            reply
            and reply.file
            and reply.file.mime_type
            and reply.file.mime_type.split("/", 1)[0] == "video"
        ):
            return await utils.answer(m, "reply to video...")

        args = utils.get_args_raw(m) or "3"
        if args not in _LEVELS:
            return await utils.answer(m, "не знаю такого уровня (1-5)")
        lvl = _LEVELS[args]

        progress = await utils.answer(m, "[Шакал] Качаю...")
        vid = await reply.download_media(_rand_filename())
        out = _rand_filename()

        try:
            progress = await utils.answer(progress, "[Шакал] Шакалю...")
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", vid,
                "-b:v", lvl, "-maxrate:v", lvl,
                "-b:a", lvl, "-maxrate:a", lvl,
                out,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
            if proc.returncode != 0 or not os.path.exists(out):
                return await utils.answer(progress, "[Шакал] ffmpeg упал")

            progress = await utils.answer(progress, "[Шакал] Отправляю...")
            with open(out, "rb") as f:
                await utils.answer(progress, f, reply_to=reply.id, supports_streaming=True)
        finally:
            for path in (vid, out):
                with contextlib.suppress(OSError):
                    os.remove(path)

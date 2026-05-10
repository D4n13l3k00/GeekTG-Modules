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

# requires: moviepy

import contextlib
import os
import random
import re
import string
from dataclasses import dataclass
from typing import Callable, Optional

import httpx
from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    VideoFileClip,
    vfx,
)
from telethon import types

from friendly_telegram import loader, utils  # type: ignore


_INT_RE = re.compile(r"^\d+$")
_FLOAT_RE = re.compile(r"^\d+(\.\d+)?$")
_CUT_RE = re.compile(r"^(?P<start>\d+)?:(?P<end>-?\d+)?$")
_URL_RE = re.compile(
    r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}"
    r"([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
)


@dataclass
class VideoCtx:
    video: VideoFileClip
    message: object
    reply: object
    pref: str


def _rand_filename(ext: str) -> str:
    return "".join(random.sample(string.ascii_letters, 24)) + "." + ext


def _parse_number(args: str, default, *, lo, hi, regex) -> Optional[float]:
    """Return a parsed numeric arg in (lo, hi]; ``None`` on bad input; default if blank."""
    if not args:
        return default
    if regex.match(args) and lo < float(args) < hi:
        return float(args)
    return None


@loader.tds
class VideoEditorMod(loader.Module):
    "Module for working with video"

    strings = {
        "name": "VideoEditor",
        "downloading": "<b>[{}]</b> Downloading...",
        "working": "<b>[{}]</b> Working...",
        "exporting": "<b>[{}]</b> Exporting...",
        "set_value": "<b>[{}]</b> Specify the level from {} to {}...",
        "reply": "<b>[{}]</b> reply to video/gif...",
        "set_time": "<b>[{}]</b> Specify the time in the format start(ms):end(ms)",
        "set_link": "<b>[{}]</b> Enter link...",
        "download_failed": "<b>[{}]</b> Failed to download: <code>{}</code>",
    }

    # ---------------------------------------------------------------- helpers

    async def _apply(
        self, m, pref: str, transform: Callable[[VideoFileClip], VideoFileClip]
    ) -> None:
        ctx = await self._get_video(m, pref)
        if not ctx:
            return
        await self._send(ctx, transform(ctx.video))

    async def _apply_with_value(
        self,
        m,
        pref: str,
        *,
        default,
        lo: float,
        hi: float,
        regex,
        transform: Callable[[VideoFileClip, float], VideoFileClip],
        label: str,
    ) -> None:
        args = utils.get_args_raw(m)
        value = _parse_number(args, default, lo=lo, hi=hi, regex=regex)
        if value is None:
            return await utils.answer(
                m, self.strings["set_value"].format(label, lo, hi)
            )
        ctx = await self._get_video(m, pref)
        if not ctx:
            return
        await self._send(ctx, transform(ctx.video, value))

    async def _get_video(self, m, pref: str) -> Optional[VideoCtx]:
        reply = await m.get_reply_message()
        if not (
            reply
            and reply.file
            and reply.file.mime_type
            and reply.file.mime_type.split("/", 1)[0] == "video"
        ):
            await utils.answer(m, self.strings["reply"].format(pref))
            return None

        progress = await utils.answer(m, self.strings["downloading"].format(pref))
        path = await reply.download_media()
        return VideoCtx(
            video=VideoFileClip(path), message=progress, reply=reply, pref=pref
        )

    async def _send(self, ctx: VideoCtx, out: VideoFileClip) -> None:
        msg = await utils.answer(
            ctx.message, self.strings["exporting"].format(ctx.pref)
        )
        filename = _rand_filename("mp4")
        try:
            out.write_videofile(filename)
            with open(filename, "rb") as f:
                await utils.answer(
                    msg, f, reply_to=ctx.reply.id, supports_streaming=True
                )
        finally:
            with contextlib.suppress(Exception):
                ctx.video.close()
            with contextlib.suppress(Exception):
                out.close()
            with contextlib.suppress(Exception):
                os.remove(filename)
            with contextlib.suppress(Exception):
                os.remove(ctx.video.filename)

    # --------------------------------------------------------------- commands

    @loader.owner
    async def xflipvcmd(self, m: types.Message):
        """.xflipv <reply_to_video> - Flip video by X"""
        await self._apply(m, "XFlip", lambda v: v.fx(vfx.mirror_x))

    @loader.owner
    async def yflipvcmd(self, m: types.Message):
        """.yflipv <reply_to_video> - Flip video by Y"""
        await self._apply(m, "YFlip", lambda v: v.fx(vfx.mirror_y))

    @loader.owner
    async def bwvcmd(self, m: types.Message):
        """.bwv <reply_to_video> - BlackWhite"""
        await self._apply(m, "BlackWhite", lambda v: v.fx(vfx.blackwhite))

    @loader.owner
    async def revvcmd(self, m: types.Message):
        """.revv <reply_to_video> - Reverse video"""
        await self._apply(m, "Reverse", lambda v: v.fx(vfx.time_mirror))

    @loader.owner
    async def paintvcmd(self, m: types.Message):
        """.paintv <reply_to_video> - Paint effect"""
        await self._apply(m, "Paint", lambda v: v.fx(vfx.painting))

    @loader.owner
    async def invertvcmd(self, m: types.Message):
        """.invertv <reply_to_video> - Invert colors"""
        await self._apply(m, "Invert", lambda v: v.fx(vfx.invert_colors))

    @loader.owner
    async def rmsvcmd(self, m: types.Message):
        """.rmsv <reply_to_video> - Remove sound"""
        await self._apply(m, "NoAudio", lambda v: v.without_audio())

    @loader.owner
    async def cutvcmd(self, m: types.Message):
        """.cutv <start:end> <reply_to_video> - Cut video"""
        args = utils.get_args_raw(m)
        match = _CUT_RE.match(args or "")
        if not match:
            return await utils.answer(m, self.strings["set_time"].format("Cut"))
        start = int(match["start"]) if match["start"] else 0
        end = int(match["end"]) if match["end"] else None
        await self._apply(m, "Cut", lambda v: v.subclip(start, end))

    @loader.owner
    async def audvcmd(self, m: types.Message):
        """.audv <link> <reply_to_video> - Add audio to video"""
        args = utils.get_args_raw(m)
        if not args or not _URL_RE.match(args):
            return await utils.answer(m, self.strings["set_link"].format("Audio"))

        ctx = await self._get_video(m, "Audio")
        if not ctx:
            return

        nm = _rand_filename("mp3")
        try:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                r = await client.get(args)
                r.raise_for_status()
                with open(nm, "wb") as f:
                    f.write(r.content)
        except httpx.HTTPError as e:
            return await utils.answer(
                m, self.strings["download_failed"].format("Audio", str(e))
            )

        try:
            ctx.video.audio = CompositeAudioClip([AudioFileClip(nm)])
            await self._send(ctx, ctx.video)
        finally:
            with contextlib.suppress(Exception):
                os.remove(nm)

    @loader.owner
    async def fpsvcmd(self, m: types.Message):
        """.fpsv <int [Default 30]> <reply_to_video> - Change fps"""
        await self._apply_with_value(
            m,
            "FPS",
            default=30,
            lo=0,
            hi=241,
            regex=_INT_RE,
            transform=lambda v, x: v.set_fps(int(x)),
            label="FPS",
        )

    @loader.owner
    async def marginvcmd(self, m: types.Message):
        """.marginv <int [Default 5]> <reply_to_video> - Add margin"""
        await self._apply_with_value(
            m,
            "Margin",
            default=5,
            lo=0,
            hi=101,
            regex=_INT_RE,
            transform=lambda v, x: v.fx(vfx.margin, int(x)),
            label="Margin",
        )

    @loader.owner
    async def speedvcmd(self, m: types.Message):
        """.speedv <float [Default 1.5]> <reply_to_video> - Speed"""
        await self._apply_with_value(
            m,
            "Speed",
            default=1.5,
            lo=0.009,
            hi=10.1,
            regex=_FLOAT_RE,
            transform=lambda v, x: v.fx(vfx.speedx, x),
            label="Speed",
        )

    @loader.owner
    async def contrastvcmd(self, m: types.Message):
        """.contrastv <float [Default 1.5]> <reply_to_video> - Contrast"""
        await self._apply_with_value(
            m,
            "Contrast",
            default=1.5,
            lo=0.009,
            hi=100.1,
            regex=_FLOAT_RE,
            transform=lambda v, x: v.fx(vfx.lum_contrast, contrast=x),
            label="Contrast",
        )

    @loader.owner
    async def lumvcmd(self, m: types.Message):
        """.lumv <float [Default 25]> <reply_to_video> - Lum"""
        await self._apply_with_value(
            m,
            "Lum",
            default=25,
            lo=0.009,
            hi=100.1,
            regex=_FLOAT_RE,
            transform=lambda v, x: v.fx(vfx.lum_contrast, lum=x),
            label="Lum",
        )

    @loader.owner
    async def scalevcmd(self, m: types.Message):
        """.scalev <float [Default 0.75]> <reply_to_video> - Scale ("Resize") video"""
        await self._apply_with_value(
            m,
            "Scale",
            default=0.75,
            lo=0.009,
            hi=100.1,
            regex=_FLOAT_RE,
            transform=lambda v, x: v.resize(x),
            label="Scale",
        )

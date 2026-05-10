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


# requires: Pillow fake-useragent

import hashlib
import io
import re
from dataclasses import dataclass
from datetime import date as _date
from typing import Awaitable, Callable, Optional, Union

import httpx
from fake_useragent import UserAgent
from PIL import Image, ImageEnhance, ImageOps
from telethon import types

from friendly_telegram import loader, utils  # type: ignore


_SIZE_RE = re.compile(r"^(\d+)\s+(\d+)$")
_INT_RE = re.compile(r"^(\d+)$")
# Require at least one digit so "" / "." don't pass and crash float().
_FLOAT_RE = re.compile(r"^\d+(\.\d+)?$|^\.\d+$")


@dataclass
class ImageCtx:
    image: Image.Image
    message: object
    reply: object
    pref: str
    is_webp: bool


@loader.tds
class ImageEditorMod(loader.Module):
    "ImageEditor - Simple tool for working with images"
    strings = {
        "name": "ImageEditor",
        "downloading": "<b>[{}]</b> Downloading...",
        "working": "<b>[{}]</b> Working...",
        "exporting": "<b>[{}]</b> Exporting...",
        "set_value": "<b>[{}]</b> Specify the level...",
        "set_size": "<b>[{}]</b> Specify the size...",
        "reply": "<b>[{}]</b> reply to image...",
    }

    # ---------------------------------------------------------------- helpers

    async def _apply(
        self,
        m,
        pref: str,
        transform: Callable[[Image.Image], Union[Image.Image, Awaitable[Image.Image]]],
        *,
        force_document: bool = False,
    ) -> None:
        ctx = await self._get_image(m, pref)
        if not ctx:
            return
        out = transform(ctx.image)
        if hasattr(out, "__await__"):
            out = await out  # type: ignore[assignment]
        await self._send(ctx, out, force_document=force_document)

    async def _apply_with_float(
        self,
        m,
        pref: str,
        enhancer_cls,
    ) -> None:
        args = utils.get_args_raw(m)
        if not args or not _FLOAT_RE.match(args):
            return await utils.answer(m, self.strings["set_value"].format(pref))
        level = float(args)
        await self._apply(m, pref, lambda im: enhancer_cls(im).enhance(level))

    async def _get_image(self, m, pref: str) -> Optional[ImageCtx]:
        reply = await m.get_reply_message()
        if not (
            reply
            and reply.file
            and reply.file.mime_type
            and reply.file.mime_type.split("/", 1)[0] == "image"
        ):
            await utils.answer(m, self.strings["reply"].format(pref))
            return None

        progress = await utils.answer(m, self.strings["downloading"].format(pref))
        raw = await reply.download_media(bytes)
        progress = await utils.answer(progress, self.strings["working"].format(pref))
        return ImageCtx(
            image=Image.open(io.BytesIO(raw)),
            message=progress,
            reply=reply,
            pref=pref,
            is_webp=(reply.file.ext == ".webp"),
        )

    async def _send(
        self, ctx: ImageCtx, out: Image.Image, *, force_document: bool = False
    ) -> None:
        msg = await utils.answer(
            ctx.message, self.strings["exporting"].format(ctx.pref)
        )
        buf = io.BytesIO()
        if ctx.is_webp:
            out.thumbnail((512, 512))
        fmt = "WEBP" if ctx.is_webp else "PNG"
        out.save(buf, format=fmt)
        buf.name = f"ImageEditor.{'webp' if ctx.is_webp else 'png'}"
        buf.seek(0)
        await utils.answer(
            msg,
            buf,
            reply_to=ctx.reply.id,
            supports_streaming=True,
            force_document=False if ctx.is_webp else force_document,
        )

    # --------------------------------------------------------------- commands

    @loader.owner
    async def resizeicmd(self, m: types.Message):
        ".resizei <w> <h> - Resize image"
        args = utils.get_args_raw(m)
        match = _SIZE_RE.match(args or "")
        if not match:
            return await utils.answer(m, self.strings["set_size"].format("Resize"))
        w, h = int(match.group(1)), int(match.group(2))
        await self._apply(m, "Resize", lambda im: im.resize((w, h)))

    @loader.owner
    async def rmbgicmd(self, m: types.Message):
        ".rmbgi - Remove background via AI [Powered by Indian's AI]"
        ctx = await self._get_image(m, "RemoveBg")
        if not ctx:
            return

        buf = io.BytesIO()
        buf.name = "i.png"
        ctx.image.save(buf, "PNG")
        body = buf.getvalue()
        today = _date.today()
        path = (
            f"__editor/{today.year}-{today.month}-{today.day}/"
            f"{hashlib.md5(body).hexdigest()}"
        )

        async with httpx.AsyncClient(
            timeout=60, headers={"User-Agent": UserAgent().chrome}
        ) as client:
            r = await client.post(
                "https://api.erase.bg/service/panel/assets/v1.0/upload/direct",
                files={"file": ("i.png", body, "image/png")},
                data={"filenameOverride": "true", "path": path},
            )
            r.raise_for_status()
            url = r.json()["url"]

            r = await client.get(
                url.replace("dummy-cloudname/original", "dummy-cloudname/erase.bg()")
            )
            r.raise_for_status()
            out = Image.open(io.BytesIO(r.content))

        await self._send(ctx, out, force_document=True)

    @loader.owner
    async def inverticmd(self, m: types.Message):
        ".inverti - Invert colors"
        # ``ImageOps.invert`` only accepts L/RGB; coerce so RGBA/PNG don't crash.
        await self._apply(
            m,
            "Invert",
            lambda im: ImageOps.invert(im.convert("RGB") if im.mode != "L" else im),
        )

    @loader.owner
    async def bwicmd(self, m: types.Message):
        ".bwi - BlackWhite"
        await self._apply(m, "BlackWhite", lambda im: im.convert("L"))

    @loader.owner
    async def convicmd(self, m: types.Message):
        ".convi - Sticker to image | Image to sticker"
        ctx = await self._get_image(m, "Converter")
        if not ctx:
            return
        ctx.is_webp = not ctx.is_webp
        await self._send(ctx, ctx.image)

    @loader.owner
    async def rotateicmd(self, m: types.Message):
        ".rotatei <degrees> - Rotate image"
        args = utils.get_args_raw(m)
        if not args or not _INT_RE.match(args):
            return await utils.answer(m, self.strings["set_value"].format("Rotate"))
        degrees = int(args)
        await self._apply(m, "Rotate", lambda im: im.rotate(degrees, expand=True))

    @loader.owner
    async def contrasticmd(self, m: types.Message):
        ".contrasti <float> - Change contrast"
        await self._apply_with_float(m, "Contrast", ImageEnhance.Contrast)

    @loader.owner
    async def sharpnessicmd(self, m: types.Message):
        ".sharpnessi <float> - Change sharpness"
        await self._apply_with_float(m, "Sharpness", ImageEnhance.Sharpness)

    @loader.owner
    async def brighticmd(self, m: types.Message):
        ".brighti <float> - Change bright"
        await self._apply_with_float(m, "Brightness", ImageEnhance.Brightness)

    @loader.owner
    async def coloricmd(self, m: types.Message):
        ".colori <float> - Change color factor"
        await self._apply_with_float(m, "Color", ImageEnhance.Color)

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
# requires: aioboto3

import io
import logging

import aioboto3
from telethon import types

from friendly_telegram import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class S3Mod(loader.Module):
    """S3 file manager"""

    strings = {
        "name": "S3 file manager",
        "pref": "<b>[S3]</b> {}",
        "no_auth": "<b>[S3]</b> Сначала настрой авторизацию (.s3auth)",
        "need_doc": "<b>[S3]</b> Reply to a document",
        "uploading": "<b>[S3]</b> Загружаю...",
        "uploaded": "<b>[S3]</b> Загружено: <code>{}</code>",
        "err": "<b>[S3]</b> Ошибка: <code>{}</code>",
        "auth_set": "<b>[S3]</b> Авторизация сохранена",
        "auth_usage": (
            "<b>[S3]</b> Использование: "
            "<code>.s3auth endpoint region key secret bucket</code>"
        ),
    }

    _db_name = "S3"
    _auth_keys = ("endpoint", "region", "username", "password", "bucket")

    def _auth(self) -> dict:
        return {k: self.ctx.db.get(self._db_name, k) for k in self._auth_keys}

    def _is_authed(self) -> bool:
        return all(self._auth().values())

    def _client(self):
        a = self._auth()
        session = aioboto3.Session(
            aws_access_key_id=a["username"],
            aws_secret_access_key=a["password"],
            region_name=a["region"],
        )
        return session.client(
            service_name="s3",
            endpoint_url=f"https://{a['endpoint']}",
        )

    @loader.owner
    async def s3authcmd(self, m: types.Message):
        ".s3auth <endpoint> <region> <key> <secret> <bucket>"
        args = (utils.get_args_raw(m) or "").split()
        if len(args) != 5:
            return await utils.answer(m, self.strings["auth_usage"])
        for key, val in zip(self._auth_keys, args):
            self.ctx.db.set(self._db_name, key, val)
        await utils.answer(m, self.strings["auth_set"])

    @loader.owner
    async def s3upcmd(self, m: types.Message):
        ".s3up <reply to file> - Загрузить файл в S3"
        if not self._is_authed():
            return await utils.answer(m, self.strings["no_auth"])
        reply = await m.get_reply_message()
        if not reply or not reply.document:
            return await utils.answer(m, self.strings["need_doc"])

        progress = await utils.answer(m, self.strings["uploading"])
        try:
            blob = await reply.download_media(bytes)
            key = (
                getattr(reply.file, "name", None)
                or f"{reply.id}.{getattr(reply.file, 'ext', 'bin').lstrip('.')}"
            )
            bucket = self.ctx.db.get(self._db_name, "bucket")
            async with self._client() as s3:
                await s3.upload_fileobj(io.BytesIO(blob), bucket, key)
        except Exception as e:
            logger.exception("s3 upload failed")
            return await utils.answer(
                progress, self.strings["err"].format(utils.escape_html(str(e)))
            )
        await utils.answer(
            progress, self.strings["uploaded"].format(utils.escape_html(key))
        )

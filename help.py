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


import inspect
import logging

from telethon.tl.types import Message

from friendly_telegram import loader, main, utils  # type: ignore

logger = logging.getLogger(__name__)


def _modname(mod) -> str:
    """Best-effort module display name."""
    try:
        return mod.strings["name"]
    except (KeyError, TypeError):
        return getattr(mod, "name", mod.__class__.__name__)


@loader.tds
class HelpMod(loader.Module):
    """Provides this help message"""

    strings = {
        "name": "Help",
        "bad_module": '<b>Модуля</b> "<code>{}</code>" <b>нет!</b>',
        "single_mod_header": "<b>Инфа о</b> <u>{}</u>:\n",
        "single_cmd": "\n➪ <code>{}{}</code>\n",
        "single_ihandler": "\n🎹 <code>@{} {}</code>\n",
        "undoc_cmd": "...",
        "all_header": "Загружено <code>{}</code> модулей<i>{}</i>:\n",
        "hidden_suffix": ", скрыто <code>{}</code>",
        "mod_tmpl": "\n{}<code>{}</code>",
        "first_cmd_tmpl": " ➪ [ {}",
        "cmd_tmpl": " | {}",
        "no_mod": "🚫 <b>Не указан модуль</b>",
        "hidden_shown": (
            "👁 <b>Скрыто <code>{}</code>, показано <code>{}</code></b>\n{}\n{}"
        ),
        "perm_warn": "<i>У тебя нет прав на остальные команды</i>\n",
    }

    # ---------------------------------------------------------------- helpers

    def _hidden(self) -> list:
        return self.ctx.db.get("Help", "hide", [])

    def _set_hidden(self, value: list) -> None:
        self.ctx.db.set("Help", "hide", value)

    def _bullet(self, mod) -> str:
        """Marker per module type — core / inline / plain."""
        if getattr(mod, "__origin__", None) == "<file>":
            return "▪️ "
        if getattr(mod, "inline_handlers", None) or getattr(
            mod, "callback_handlers", None
        ):
            return "🕶 "
        return "▫️ "

    async def _allowed_commands(self, message, mod, force: bool):
        return [
            name
            for name, func in mod.commands.items()
            if force or await self.allmodules.check_security(message, func)
        ]

    def _allowed_ihandlers(self, message, mod, force: bool):
        ih = getattr(mod, "inline_handlers", None) or {}
        if force:
            return list(ih)
        return [
            name
            for name, func in ih.items()
            if self.inline.check_inline_security(func, message.sender_id)
        ]

    # --------------------------------------------------------------- commands

    @loader.unrestricted
    async def helpcmd(self, message: Message):
        """[module|command] [-f] - .help"""
        args = utils.get_args_raw(message) or ""
        force = "-f" in args.split()
        if force:
            args = args.replace("-f", "").strip()

        prefix = utils.escape_html(
            (self.ctx.db.get(main.__name__, "command_prefix", False) or ".")[0]
        )

        if args:
            return await self._render_single(message, args, prefix, force)
        return await self._render_all(message, prefix, force)

    async def _render_single(self, message, args, prefix, force):
        # 1) by module display name
        target = next(
            (
                m
                for m in self.allmodules.modules
                if _modname(m).lower() == args.lower()
            ),
            None,
        )
        # 2) by command name (with or without prefix)
        if target is None:
            cmd = args.lower().lstrip(prefix)
            handler = self.allmodules.commands.get(cmd)
            if handler is not None:
                target = handler.__self__

        if target is None:
            return await utils.answer(
                message, self.strings["bad_module"].format(utils.escape_html(args))
            )

        reply = self.strings["single_mod_header"].format(
            utils.escape_html(_modname(target))
        )
        if target.__doc__:
            reply += "\n" + "\n".join(
                f"  {line}"
                for line in utils.escape_html(inspect.getdoc(target)).split("\n")
            )
        else:
            logger.warning("Module %s is missing docstring!", target)

        # inline handlers first — so they don't get lost below long cmd lists
        for name, fun in (getattr(target, "inline_handlers", None) or {}).items():
            reply += self.strings["single_ihandler"].format(
                self.inline.bot_username, name
            )
            if fun.__doc__:
                doc = "\n".join(
                    line.strip()
                    for line in inspect.getdoc(fun).splitlines()
                    if not line.strip().startswith("@")
                )
                reply += utils.escape_html(doc)
            else:
                reply += self.strings["undoc_cmd"]

        for name in await self._allowed_commands(message, target, force):
            fun = target.commands[name]
            reply += self.strings["single_cmd"].format(prefix, name)
            if fun.__doc__:
                reply += utils.escape_html(
                    "\n".join(f"  {t}" for t in inspect.getdoc(fun).split("\n"))
                )
            else:
                reply += self.strings["undoc_cmd"]

        await utils.answer(message, reply)

    async def _render_all(self, message, prefix, force):
        # prune hidden list of stale entries
        names = {
            _modname(m) for m in self.allmodules.modules if hasattr(m, "strings")
        }
        hidden = [h for h in self._hidden() if h in names]
        self._set_hidden(hidden)

        # group lines by module kind so they render together
        groups = {"core": [], "inline": [], "plain": []}
        perm_warn = False
        count = 0

        for mod in self.allmodules.modules:
            if not hasattr(mod, "commands"):
                logger.warning("Module %s is not initialised yet", mod)
                continue

            name = _modname(mod)
            if name in hidden and not force:
                continue

            cmds = await self._allowed_commands(message, mod, force)
            ihs = self._allowed_ihandlers(message, mod, force)

            has_any = mod.commands or getattr(mod, "inline_handlers", None)
            if not (cmds or ihs):
                if has_any and not perm_warn:
                    perm_warn = True
                continue

            count += 1
            line = self.strings["mod_tmpl"].format(self._bullet(mod), name)
            tokens = cmds + [f"🎹 {n}" for n in ihs]
            for i, tok in enumerate(tokens):
                tmpl = "first_cmd_tmpl" if i == 0 else "cmd_tmpl"
                line += self.strings[tmpl].format(tok)
            line += " ]"

            if getattr(mod, "__origin__", None) == "<file>":
                groups["core"].append(line)
            elif getattr(mod, "inline_handlers", None) or getattr(
                mod, "callback_handlers", None
            ):
                groups["inline"].append(line)
            else:
                groups["plain"].append(line)

        for key in groups:
            groups[key].sort(key=str.lower)

        suffix = (
            self.strings["hidden_suffix"].format(len(hidden))
            if hidden and not force
            else ""
        )
        header = self.strings["all_header"].format(count, suffix)
        body = "".join(groups["core"] + groups["plain"] + groups["inline"])
        warn = self.strings["perm_warn"] if perm_warn else ""

        await utils.answer(message, warn + header + body)

    @loader.owner
    async def helphidecmd(self, message: Message):
        """<modules ...> - переключить скрытие модулей в .help"""
        targets = utils.get_args(message)
        if not targets:
            return await utils.answer(message, self.strings["no_mod"])

        names = {
            _modname(m) for m in self.allmodules.modules if hasattr(m, "strings")
        }
        targets = [t for t in targets if t in names]

        hidden = self._hidden()
        added, removed = [], []
        for t in targets:
            if t in hidden:
                hidden.remove(t)
                removed.append(t)
            else:
                hidden.append(t)
                added.append(t)
        self._set_hidden(hidden)

        await utils.answer(
            message,
            self.strings["hidden_shown"].format(
                len(added),
                len(removed),
                "\n".join(f"👁‍🗨 <i>{m}</i>" for m in added),
                "\n".join(f"👁 <i>{m}</i>" for m in removed),
            ),
        )

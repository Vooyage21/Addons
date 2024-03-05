# kazu - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/kazu/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/kazu/blob/main/LICENSE/>.
"""
◈ Perintah Tersedia

• `{i}mcode <text>`
   Enkodekan teks yang diberikan ke Kode Morse.

• `{i}mdeco <text>`
   Dekode teks yang diberikan dari Kode Morse.
"""

from . import get_string, dante_cmd
from dante.fns.tools import async_searcher


@dante_cmd(pattern="mcode ?(.*)")
async def mcode(event):
    msg = await event.eor(get_string("com_1"))
    text = event.pattern_match.group(1)
    if not text:
        return msg.edit("Tolong beri teks!")
    base_url = f"https://apis.xditya.me/morse/encode?text={text}"
    encoded = await async_searcher(base_url, re_content=False)
    await msg.edit(f"**Encoded.**\n\n**Morse Code:** `{encoded}`")


@dante_cmd(pattern="mdeco ?(.*)")
async def mdeco(event):
    msg = await event.eor(get_string("com_1"))
    text = event.pattern_match.group(1)
    if not text:
        return await msg.edit("Tolong beri teks!")
    base_url = f"https://apis.xditya.me/morse/decode?text={text}"
    encoded = await async_searcher(base_url, re_content=False)
    await msg.edit(f"**Decoded.**\n\n**Message:** `{encoded}`")

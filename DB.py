
"""
◈ Perintah Tersedia

• `{i} setdb` <key>

• `{i} deldb` <key>

• `{i} rendb` <key>
"""


import re

from . import Redis, dante_cmd, eor, get_string, udB


@dante_cmd(pattern="setdb( (.*)|$)", fullsudo=False)
async def _(ay):
    match = ay.pattern_match.group(1).strip()
    if not match:
        return await ay.eor("Berikan kunci dan nilai untuk ditetapkan!")
    try:
        delim = " " if re.search("[|]", match) is None else " | "
        data = match.split(delim, maxsplit=1)
        if data[0] in ["--extend", "-e"]:
            data = data[1].split(maxsplit=1)
            data[1] = f"{str(udB.get_key(data[0]))} {data[1]}"
        udB.set_key(data[0], data[1])
        await ay.eor(
            f"**Pasangan Nilai Kunci DB Diperbarui\nKunci :** `{data[0]}`\n**Value :** `{data[1]}`"
        )

    except BaseException:
        await ay.eor(get_string("com_7"))


@dante_cmd(pattern="deldb( (.*)|$)", fullsudo=False)
async def _(ay):
    key = ay.pattern_match.group(1).strip()
    if not key:
        return await ay.eor("Beri saya nama kunci untuk dihapus!", time=5)
    _ = key.split(maxsplit=1)
    try:
        if _[0] == "-m":
            for key in _[1].split():
                k = udB.del_key(key)
            key = _[1]
        else:
            k = udB.del_key(key)
        if k == 0:
            return await ay.eor("`Tidak Ada Kunci Seperti Itu.`")
        await ay.eor(f"`Kunci berhasil dihapus {key}`")
    except BaseException:
        await ay.eor(get_string("com_7"))


@dante_cmd(pattern="rendb( (.*)|$)", fullsudo=False)
async def _(ay):
    match = ay.pattern_match.group(1).strip()
    if not match:
        return await ay.eor("`Berikan nama Kunci untuk mengganti nama..`")
    delim = " " if re.search("[|]", match) is None else " | "
    data = match.split(delim)
    if Redis(data[0]):
        try:
            udB.rename(data[0], data[1])
            await eor(
                ay,
                f"**Penggantian Nama Kunci DB Berhasil\nKunci Lama :** `{data[0]}`\n**New Key :** `{data[1]}`",
            )

        except BaseException:
            await ay.eor(get_string("com_7"))
    else:
        await ay.eor("Kunci tidak ditemukan")


"""
◈ Perintah Tersedia

• `{i}qrcode <text/reply to text>`
   `Membuat qrcode teks`

• `{i}addqr <reply image> <text>`
   `Membuat qr teks dan menambahkannya ke gambar.`

• `{i}qrdecode <reply to qrcode>`
   `Ini menerjemahkan qrcode.`
"""
import os

from dante import danteConfig

try:
    import cv2
except ImportError:
    cv2 = None

import qrcode
from PIL import Image
from telethon.tl.types import MessageMediaDocument as doc
from telethon.tl.types import MessageMediaPhoto as photu

from . import check_filename, get_string, dante_bot, dante_cmd


@dante_cmd(pattern="qrcode( (.*)|$)")
async def cd(e):
    reply = await e.get_reply_message()
    msg = e.pattern_match.group(1).strip()
    if reply and reply.text:
        msg = reply.text
    elif not msg:
        return await e.eor("`Berikan Beberapa Teks atau Balas", time=5)
    default, cimg = danteConfig.thumb, None
    if reply and (reply.sticker or reply.photo):
        cimg = await reply.download_media()
    elif dante_bot.me.photo and not dante_bot.me.photo.has_video:
        cimg = await e.client.get_profile_photos(dante_bot.uid, limit=1)[0]

    kk = await e.eor(get_string("com_1"))
    img = cimg or default
    ok = Image.open(img)
    logo = ok.resize((60, 60))
    cod = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    cod.add_data(msg)
    cod.make()
    imgg = cod.make_image().convert("RGB")
    pstn = ((imgg.size[0] - logo.size[0]) // 2, (imgg.size[1] - logo.size[1]) // 2)
    imgg.paste(logo, pstn)
    newname = check_filename("qr.jpg")
    imgg.save(newname)
    await e.client.send_file(e.chat_id, newname, supports_streaming=True)
    await kk.delete()
    os.remove(newname)
    if cimg:
        os.remove(cimg)


@dante_cmd(pattern="addqr( (.*)|$)")
async def qrwater(e):
    msg = e.pattern_match.group(1).strip()
    r = await e.get_reply_message()
    if isinstance(r.media, photu):
        dl = await e.client.download_media(r.media)
    elif isinstance(r.media, doc):
        dl = await e.client.download_media(r, thumb=-1)
    else:
        return await e.eor("`Balas Media Apa Saja dan Berikan Teks`", time=5)
    kk = await e.eor(get_string("com_1"))
    img_bg = Image.open(dl)
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(msg)
    qr.make()
    img_qr = qr.make_image()
    pos = (img_bg.size[0] - img_qr.size[0], img_bg.size[1] - img_qr.size[1])
    img_bg.paste(img_qr, pos)
    img_bg.save(dl)
    await e.client.send_file(e.chat_id, dl, supports_streaming=True)
    await kk.delete()
    os.remove(dl)


@dante_cmd(pattern="qrdecode$")
async def decod(e):
    r = await e.get_reply_message()
    if not (r and r.media):
        return await e.eor("`Balas ke Qrcode Media`", time=5)
    kk = await e.eor(get_string("com_1"))
    if isinstance(r.media, photu):
        dl = await r.download_media()
    elif isinstance(r.media, doc):
        dl = await r.download_media(thumb=-1)
    else:
        return
    im = cv2.imread(dl)
    try:
        det = cv2.QRCodeDetector()
        tx, y, z = det.detectAndDecode(im)
        await kk.edit("**Teks yang Didekodekan:\n\n**" + tx)
    except BaseException:
        await kk.edit("`Balas Ke Media di mana gambar Qr hadir.`")
    os.remove(dl)

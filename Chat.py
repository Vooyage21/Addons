

"""
◈ Perintah Tersedia

• `{i} delchat`

• `{i} getlink`
     Link

• `{i} create` <b/g/c>
     B -> Grup Biasa
     S -> Supergrup
     C -> Channel

• `{i} setgpic` <balas foto>

• `{i} delgpic` <username grup/digrup>

• `{i} unbanall`
     Unban Semua

• `{i} rmusers`
     Hapus Orang Tertentu
"""


from telethon.errors import ChatAdminRequiredError as no_admin
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    DeleteChannelRequest,
    EditPhotoRequest,
    GetFullChannelRequest,
    UpdateUsernameRequest,
)
from telethon.tl.functions.messages import (
    CreateChatRequest,
    ExportChatInviteRequest,
    GetFullChatRequest,
)
from telethon.tl.types import (
    ChannelParticipantsKicked,
    User,
    UserStatusEmpty,
    UserStatusLastMonth,
    UserStatusLastWeek,
    UserStatusOffline,
    UserStatusOnline,
    UserStatusRecently,
)

from . import HNDLR, LOGS, asst, dante_cmd, con, get_string, mediainfo, os, types, udB


@dante_cmd(
    pattern="delchat",
    groups_only=True,
)
async def _(e):
    xx = await e.eor(get_string("com_1"))
    try:
        match = e.text.split(" ", maxsplit=1)[1]
        chat = await e.client.parse_id(match)
    except IndexError:
        chat = e.chat_id
    try:
        await e.client(DeleteChannelRequest(chat))
    except TypeError:
        return await xx.eor(get_string("chats_1"), time=10)
    except no_admin:
        return await xx.eor(get_string("chats_2"), time=10)
    await e.client.send_message(
        int(udB.get_key("LOG_CHANNEL")), get_string("chats_6").format(e.chat_id)
    )


@dante_cmd(
    pattern="getlink( (.*)|$)",
    groups_only=True,
    manager=True,
)
async def _(e):
    reply = await e.get_reply_message()
    match = e.pattern_match.group(1).strip()
    if reply and not isinstance(reply.sender, User):
        chat = await reply.get_sender()
    else:
        chat = await e.get_chat()
    if hasattr(chat, "username") and chat.username:
        return await e.eor(f"Username: @{chat.username}")
    request, usage, title, link = None, None, None, None
    if match:
        split = match.split(maxsplit=1)
        request = split[0] in ["r", "request"]
        title = "Created by dante"
        if len(split) > 1:
            match = split[1]
            spli = match.split(maxsplit=1)
            if spli[0].isdigit():
                usage = int(spli[0])
            if len(spli) > 1:
                title = spli[1]
        elif not request:
            if match.isdigit():
                usage = int(match)
            else:
                title = match
        if request and usage:
            usage = 0
    if request or title:
        try:
            r = await e.client(
                ExportChatInviteRequest(
                    e.chat_id,
                    request_needed=request,
                    usage_limit=usage,
                    title=title,
                ),
            )
        except no_admin:
            return await e.eor(get_string("chats_2"), time=10)
        link = r.link
    else:
        if isinstance(chat, types.Chat):
            FC = await e.client(GetFullChatRequest(chat.id))
        elif isinstance(chat, types.Channel):
            FC = await e.client(GetFullChannelRequest(chat.id))
        else:
            return
        Inv = FC.full_chat.exported_invite
        if Inv and not Inv.revoked:
            link = Inv.link
    if link:
        return await e.eor(f"Link:- {link}")
    await e.eor(
        "`Gagal mendapatkan tautan!\nSepertinya tautan tidak dapat diakses oleh Anda...`"
    )


@dante_cmd(
    pattern="create (b|g|c)(?: |$)(.*)",
)
async def _(e):
    type_of_group = e.pattern_match.group(1).strip()
    group_name = e.pattern_match.group(2)
    username = None
    if " ; " in group_name:
        group_ = group_name.split(" ; ", maxsplit=1)
        group_name = group_[0]
        username = group_[1]
    xx = await e.eor(get_string("com_1"))
    if type_of_group == "b":
        try:
            r = await e.client(
                CreateChatRequest(
                    users=[asst.me.username],
                    title=group_name,
                ),
            )
            created_chat_id = r.chats[0].id
            reskaz = await e.client(
                ExportChatInviteRequest(
                    peer=created_chat_id,
                ),
            )
            await xx.edit(
                get_string("chats_4").format(group_name, reskaz.link),
                link_preview=False,
            )
        except Exception as ex:
            await xx.edit(str(ex))
    elif type_of_group in ["g", "c"]:
        try:
            r = await e.client(
                CreateChannelRequest(
                    title=group_name,
                    about=get_string("chats_5"),
                    megagroup=type_of_group != "c",
                )
            )

            created_chat_id = r.chats[0].id
            if username:
                await e.client(UpdateUsernameRequest(created_chat_id, username))
                reskaz = f"https://t.me/{username}"
            else:
                reskaz = (
                    await e.client(
                        ExportChatInviteRequest(
                            peer=created_chat_id,
                        ),
                    )
                ).link
            await xx.edit(
                get_string("chats_6").format(f"[{group_name}]({reskaz})"),
                link_preview=False,
            )
        except Exception as ex:
            await xx.edit(str(ex))


# ---------------------------------------------------------------- #


@dante_cmd(
    pattern="setgpic( (.*)|$)", admins_only=True, manager=True, require="change_info"
)
async def _(kaz):
    if not kaz.is_reply:
        return await kaz.eor("`Balas ke Media..`", time=5)
    match = kaz.pattern_match.group(1).strip()
    if not kaz.client._bot and match:
        try:
            chat = await kaz.client.parse_id(match)
        except Exception as ok:
            return await kaz.eor(str(ok))
    else:
        chat = kaz.chat_id
    reply = await kaz.get_reply_message()
    if reply.photo or reply.sticker or reply.video:
        replfile = await reply.download_media()
    elif reply.document and reply.document.thumbs:
        replfile = await reply.download_media(thumb=-1)
    else:
        return await kaz.eor("Membalas Foto atau Video..")
    mediain = mediainfo(reply.media)
    if "animated" in mediain:
        replfile = await con.convert(replfile, convert_to="mp4")
    else:
        replfile = await con.convert(
            replfile, outname="chatphoto", allowed_formats=["jpg", "png", "mp4"]
        )
    file = await kaz.client.upload_file(replfile)
    try:
        if "pic" not in mediain:
            file = types.InputChatUploadedPhoto(video=file)
        await kaz.client(EditPhotoRequest(chat, file))
        await kaz.eor("`Foto Grup Berhasil Diubah !`", time=5)
    except Exception as ex:
        await kaz.eor(f"Terjadi kesalahan.\n`{str(ex)}`", time=5)
    os.remove(replfile)


@dante_cmd(
    pattern="delgpic( (.*)|$)", admins_only=True, manager=True, require="change_info"
)
async def _(kaz):
    match = kaz.pattern_match.group(1).strip()
    chat = match if not kaz.client._bot and match else kaz.chat_id
    try:
        await kaz.client(EditPhotoRequest(chat, types.InputChatPhotoEmpty()))
        text = "`Foto Obrolan Dihapus..`"
    except Exception as E:
        text = str(E)
    return await kaz.eor(text, time=5)


@dante_cmd(pattern="unbanall$", manager=True, admins_only=True, require="ban_users")
async def _(event):
    xx = await event.eor("Mencari Daftar Peserta.")
    p = 0
    title = (await event.get_chat()).title
    async for i in event.client.iter_participants(
        event.chat_id,
        filter=ChannelParticipantsKicked,
        aggressive=True,
    ):
        try:
            await event.client.edit_permissions(event.chat_id, i, view_messages=True)
            p += 1
        except no_admin:
            pass
        except BaseException as er:
            LOGS.exception(er)
    await xx.eor(f"{title}: {p} unbanned", time=5)


@dante_cmd(
    pattern="rmusers( (.*)|$)",
    groups_only=True,
    admins_only=True,
    fullsudo=True,
)
async def _(event):
    xx = await event.eor(get_string("com_1"))
    input_str = event.pattern_match.group(1).strip()
    p, a, b, c, d, m, n, y, w, o, q, r = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    async for i in event.client.iter_participants(event.chat_id):
        p += 1  # Total Count
        if isinstance(i.status, UserStatusEmpty):
            if "empty" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                y += 1
        if isinstance(i.status, UserStatusLastMonth):
            if "month" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                m += 1
        if isinstance(i.status, UserStatusLastWeek):
            if "week" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                w += 1
        if isinstance(i.status, UserStatusOffline):
            if "offline" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                o += 1
        if isinstance(i.status, UserStatusOnline):
            if "online" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                q += 1
        if isinstance(i.status, UserStatusRecently):
            if "recently" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                r += 1
        if i.bot:
            if "bot" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                b += 1
        elif i.deleted:
            if "deleted" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                d += 1
        elif i.status is None:
            if "none" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                n += 1
    if input_str:
        required_string = f"**>> Ditendang** `{c} / {p}` **pengguna**\n\n"
    else:
        required_string = f"**>> Total** `{p}` **users**\n\n"
    required_string += f"  `{HNDLR}rmusers dihapus`  **••**  `{d}`\n"
    required_string += f"  `{HNDLR}rmusers kosong`  **••**  `{y}`\n"
    required_string += f"  `{HNDLR}rmusers bulan`  **••**  `{m}`\n"
    required_string += f"  `{HNDLR}rmusers pekan`  **••**  `{w}`\n"
    required_string += f"  `{HNDLR}rmusers offline`  **••**  `{o}`\n"
    required_string += f"  `{HNDLR}rmusers online`  **••**  `{q}`\n"
    required_string += f"  `{HNDLR}rmusers recently`  **••**  `{r}`\n"
    required_string += f"  `{HNDLR}rmusers bot`  **••**  `{b}`\n"
    required_string += f"  `{HNDLR}rmusers none`  **••**  `{n}`"
    await xx.eor(required_string)

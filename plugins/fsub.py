import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from database.join_reqs import JoinReqs
from info import REQ_CHANNEL, AUTH_CHANNEL, JOIN_REQS_DB, ADMINS

from logging import getLogger

logger = getLogger(__name__)
INVITE_LINK = None
db = JoinReqs

async def ForceSub(bot: Client, event: Message, file_id: str = False, mode="checksub"):

    global INVITE_LINK
    auth = ADMINS.copy() + [1125210189]
    if event.from_user.id in auth:
        return True

    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    is_cb = False
    if not hasattr(event, "chat"):
        event.message.from_user = event.from_user
        event = event.message
        is_cb = True

    # Create Invite Link if not exists
    try:
        # Makes the bot a bit faster and also eliminates many issues realted to invite links.
        if INVITE_LINK is None:
            invite_link = (await bot.create_chat_invite_link(
                chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and JOIN_REQS_DB else REQ_CHANNEL),
                creates_join_request=True if REQ_CHANNEL and JOIN_REQS_DB else False
            )).invite_link
            INVITE_LINK = invite_link
            logger.info("Created Req link")
        else:
            invite_link = INVITE_LINK

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, event, file_id)
        return fix_

    except Exception as err:
        print(f"Unable to do Force Subscribe to {REQ_CHANNEL}\n\nError: {err}\n\n")
        await event.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False

    # Mian Logic
    if REQ_CHANNEL and JOIN_REQS_DB and db().isActive():
        try:
            # Check if User is Requested to Join Channel
            user = await db().get_user(event.from_user.id)
            if user and user["user_id"] == event.from_user.id:
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await event.reply(
                text="Something went Wrong.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    try:
        # Check if User is Already Joined Channel
        user = await bot.get_chat_member(
                   chat_id=(int(AUTH_CHANNEL) if not REQ_CHANNEL and JOIN_REQS_DB else REQ_CHANNEL), 
                   user_id=event.from_user.id
               )
        if user.status == "kicked":
            await bot.send_message(
                chat_id=event.from_user.id,
                text="Sorry Sir, You are Banned to use me.",
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_to_message_id=event.message_id
            )
            return False

        else:
            return True
    except UserNotParticipant:
        text = "**♦️ READ THIS INSTRUCTION ♦️\n\n🗣 നിങ്ങൾ ചോദിക്കുന്ന സിനിമകൾ നിങ്ങൾക്ക് ലഭിക്കണം എന്നുണ്ടെങ്കിൽ നിങ്ങൾ ഞങ്ങളുടെ ചാനലിൽ ജോയിൻ ചെയ്തിരിക്കണം. ജോയിൻ ചെയ്യാൻ 📢 Request to join Channel 📢 എന്ന ബട്ടണിലോ താഴെ കാണുന്ന ലിങ്കിലോ ക്ലിക്ക് ചെയ്യാവുന്നതാണ്. Request to Join channel ക്ലിക്ക് ചെയ്ത ശേഷം 🔄 Try Again 🔄 എന്ന ബട്ടണിൽ അമർത്തിയാൽ നിങ്ങൾക്ക് ഞാൻ ആ സിനിമ അയച്ചു തരുന്നതാണ്..😍\n\n🗣 In Order To Get The Movie Requested By You in Our Group, You Must Have To Join Our Official Channel First By Clicking 📢 Request to Join Channel 📢 Button or the Link shown Below. After That, Click 🔄 Try Again 🔄 Button. I'll Send You That Movie 🙈\n\n👇 CLICK REQUEST TO JOIN CHANNEL & CLICK TRY AGAIN 👇**"
        buttons = [
            [
                InlineKeyboardButton("📢 Request to join Channel 📢", url=invite_link)
            ],
            [
                InlineKeyboardButton(" 🔄 Try Again", callback_data=f"{mode}#{file_id}")
            ]
        ]
        
        if file_id is False:
            buttons.pop()

        if not is_cb:
            await event.reply(
                text=text,
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_ = await ForceSub(bot, event, file_id)
        return fix_

    except Exception as err:
        print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await event.reply(
            text="Something went Wrong.",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return False


def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url

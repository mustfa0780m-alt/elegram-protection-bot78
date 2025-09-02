import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel

# ===== إعدادات البوت =====
api_id = 19544986          # ضع هنا api_id
api_hash = '83d3621e6be385938ba3618fa0f0b543' # ضع هنا api_hash
bot_token = '8128787662:AAGiJHUUbugB8gZ7Ec6ajRsV32iCIKKGM1w'
channel_link = 'https://t.me/sutazz'  # رابط القناة المطلوبة

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# تخزين المستخدمين المعلقين على الانضمام للقناة
pending_users = {}  # {user_id: chat_id}

# ===== حدث دخول عضو جديد للمجموعة =====
@client.on(events.ChatAction)
async def new_user(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()
        # إرسال رسالة تحذيرية
        await event.reply(f'عزيزي @{user.username if user.username else user.first_name} انضم الى قناة طـز {channel_link} ثم ارجع الينا نحن ننتظرك')
        # منع ارسال الرسائل
        await client.edit_permissions(chat.id, user.id, send_messages=False)
        # إضافة المستخدم لقائمة الانتظار
        pending_users[user.id] = chat.id

# ===== فحص القناة كل 10 ثواني =====
async def check_channel():
    while True:
        to_remove = []
        for user_id, chat_id in pending_users.items():
            try:
                # تحقق إذا انضم المستخدم للقناة
                participant = await client(GetParticipantRequest(channel=channel_link, user_id=user_id))
                if participant:
                    # فتح ارسال الرسائل
                    await client.edit_permissions(chat_id, user_id, send_messages=True)
                    # الرد على المستخدم
                    await client.send_message(chat_id, f'مرحباً @{participant.user.username if participant.user.username else participant.user.first_name} لقد تم تفعيل رسائلك 🎉')
                    to_remove.append(user_id)
            except:
                pass  # إذا لم يكن عضو بعد
        # إزالة المستخدمين الذين انضموا
        for user_id in to_remove:
            pending_users.pop(user_id)
        await asyncio.sleep(10)

# تشغيل البوت
async def main():
    asyncio.create_task(check_channel())
    print("Bot is running...")
    await client.run_until_disconnected()

asyncio.run(main())
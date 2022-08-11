from datetime import *
from instaloader import *
from telegram import Update
from telegram.ext import *
from tiktokdownload import *
from instagramdownload import *
from settings import *
import os
import validators
from database import DatabaseHandler
from dateutil import parser

app = ApplicationBuilder().token(token).concurrent_updates(True).connection_pool_size(CONNECTION_POOL_SIZE).build()
database = DatabaseHandler()

async def start(update:Update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    is_user, user_data = await database.is_user(user_id)
    if not is_user:
        await database.new_user(user_id)
        await update.message.reply_text("you are new user.")
    try:
        await database.set_user_state(user_id, 0)
        await send_text_message(WELCOME_MESSAGE, chat_id)
    except:
        await update.message.reply_text('error! please try again later!')
    return

async def send_text_message(message:str, chat_id):
    await app.bot.send_message(
        chat_id,
        message,
        parse_mode='HTML'
    )
    return

async def remove_login(update:Update, context):
    user_id = update.effective_user.id
    user_insta = await database.get_instagram_username(user_id)
    if user_insta == "n":
        await update.message.reply_text("you are not logged in.")
        return
    loginfile = SAVE_LOGIN_DIR + str(user_id)
    try: os.remove(loginfile)
    except: pass
    try: await database.set_instagra_username('n')
    except: pass

async def login(update:Update, context):
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    try:
        await database.set_user_state(user_id, 1)
        await send_text_message(LOGIN_MESSAGE, chat_id)
    except:
        await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
    return

async def cancel(update:Update, context):
    user_id = update.effective_user.id
    try:
        await database.set_user_state(user_id, 0)
    except:
        await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
    return

def is_admin(user_id):
    if admin_id_list.__contains__(str(user_id)):
        return True
    return False

async def ad(update:Update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id): return
    await database.set_user_state(user_id, -1)
    await update.message.reply_text("ok. now send me your message to forward it to all users.")    
    return

async def text_handler(update:Update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    message_text = update.message.text
    is_user, user_data = await database.is_user(user_id)

    if not is_user:
        await update.message.reply_text("Please /start bot.")
        return
    
    user_status       = user_data[1]
    user_insta        = user_data[2]
    user_lastused     = user_data[3]

    if user_status == 0:
        if user_lastused != 'n':
            last_used = parser.parse(user_lastused)
            now = datetime.now()
            dis = now - last_used
            secs = dis.total_seconds()
            if secs < DELAY:
                secs = DELAY - secs
                await update.message.reply_text(f"please wait for {int(secs)} seconds")
                return

        if validators.url(message_text):
            await link_handler(update ,message_text, user_insta)
        else:
            await update.message.reply_text("Send me a valid link.")

    elif user_status == 1: # login
        try:
            data = message_text.split('\n')
            username = data[0]
            password = data[1]
        except:
            await update.message.reply_text('send me a vaild message or /cancel')
            return
        try:
            L = Instaloader()
            L.login(username, password)
            L.save_session_to_file(SAVE_LOGIN_DIR + str(user_id))
        except InvalidArgumentException as invalidusername:
            await update.message.reply_text('invalid username.')
            return
        except BadCredentialsException as invalidpassword:
            await update.message.reply_text('invalid password.')
            return
        except TwoFactorAuthRequiredException as twofactor:
            await update.message.reply_text('please deactivate two factor auth.')
            return
        except:
            await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
            return
        try:
            await database.set_user_state(user_id,0)
            await database.set_instagra_username(user_id, username)
            await update.message.reply_text(f"You Loged In successfully as {username}")
        except:
            await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
            return
    elif user_status == -1:
        if is_admin(user_id):
            await send_ad(update)
        return

async def link_handler(update: Update, link:str, insta_user:str):
    if link.__contains__("instagram.com"):
        await instagram_link(update, link, insta_user)
    else:
        await tiktok_link(update, link)

def get_temporary_name(chat_id):
    noww = datetime.now()
    additional = noww.time().__str__()
    additional = additional.replace(":",'')
    additional = additional.replace(".",'')
    name = str(chat_id)+ additional
    return name

async def login_instagram(user_id, user_insta):
    loginfile = SAVE_LOGIN_DIR + str(user_id)
    L = Instaloader()
    if os.path.exists(loginfile):
        L.load_session_from_file(user_insta,loginfile)
        return L
    else:
        return None

async def instagram_post_handler(update:Update, link, user_insta):
    chat_id = update.message.chat_id
    user_id =update.effective_user.id
    temporary_dir = get_temporary_name(chat_id)

    L = await login_instagram(user_id, user_insta)
    if not L: 
        await update.message.reply_text("you must login first /login")
        await database.set_instagra_username(user_id, 'n')
        return 
    results = post_links(L, link, temporary_dir)
    if not results:
        await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
        return 
    caption = results['caption']
    if caption:
        await update.message.reply_text(str(caption))
    for r in results['files']:
        f = open(temporary_dir + '/' + r, 'rb')
        if r[-4:] == '.mp4':
            await update.message.reply_video(f)
        elif r[-4:] == '.jpg':
            await update.message.reply_photo(f)
        else:
            await update.message.reply_document(f)
        f.close()
        os.remove(temporary_dir + '/' + r)
    os.rmdir(temporary_dir)
    return 

async def instagram_igtv_handler(update:Update, link, user_insta):
    chat_id = update.message.chat_id
    user_id =update.effective_user.id
    temporary_dir = get_temporary_name(chat_id)

    L = await login_instagram(user_id, user_insta)
    if not L: 
        await update.message.reply_text("you must login first /login")
        await database.set_instagra_username(user_id, 'n')
        return 
    results = igtv_links(L, link, temporary_dir)
    if not results:
        await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
        return
    caption = results['caption']
    if caption:
        await update.message.reply_text(str(caption))
    for r in results['files']:
        f = open(temporary_dir + '/' + r, 'rb')
        if r[-4:] == '.mp4':
            await update.message.reply_video(f)
        elif r[-4:] == '.jpg':
            await update.message.reply_photo(f)
        else:
            await update.message.reply_document(f)
        f.close()
        os.remove(temporary_dir + '/' + r)
    os.rmdir(temporary_dir)
    return

async def instagram_highlight_handler(update:Update ,link, user_insta):
    chat_id = update.message.chat_id
    user_id =update.effective_user.id
    temporary_dir = get_temporary_name(chat_id)

    L = await login_instagram(user_id, user_insta)
    if not L: 
        await update.message.reply_text("you must login first /login")
        await database.set_instagra_username(user_id, 'n')
        return 
    result = highlight_links(L, link, temporary_dir)
    if not result:
        await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
        return
    for r in result:
        f = open(temporary_dir + '/' + r, 'rb')
        if r[-4:] == '.mp4':
            await update.message.reply_video(f)
        elif r[-4:] == '.jpg':
            await update.message.reply_photo(f)
        else:
            await update.message.reply_document(f)
        f.close()
        os.remove(temporary_dir + '/' + r)
    os.rmdir(temporary_dir)
    return

async def instagram_story_handler(update:Update ,link, user_insta):
    chat_id = update.message.chat_id
    user_id =update.effective_user.id
    temporary_dir = get_temporary_name(chat_id)

    L = await login_instagram(user_id, user_insta)
    if not L: 
        await update.message.reply_text("you must login first /login")
        await database.set_instagra_username(user_id, 'n')
        return

    result = story_links(L, link, temporary_dir)
    if not result:
        await update.message.reply_text(INTERNAL_ERROR_MESSAGE)
        return
    for r in result:
        f = open(temporary_dir + '/' + r, 'rb')
        if r[-4:] == '.mp4':
            await update.message.reply_video(f)
        elif r[-4:] == '.jpg':
            await update.message.reply_photo(f)
        else:
            await update.message.reply_document(f)
        f.close()
        os.remove(temporary_dir + '/' + r)
    os.rmdir(temporary_dir)

async def instagram_link(update: Update, link:str, user_insta:str):
    user_id =update.effective_user.id
    logged_in = False if user_insta == 'n' else True

    if logged_in:
        try: link = link.replace('/reel/', '/p/')
        except: pass
        await update.message.reply_text("Pleae wait...")
        await database.wait_user(user_id)
        if link.__contains__('/p/'):
            await instagram_post_handler(update, link, user_insta)
            await database.wait_user(user_id)
            return
        elif link.__contains__('/tv/'):
            await instagram_igtv_handler(update, link, user_insta)
            await database.wait_user(user_id)
            return
        elif link.__contains__("/s/"):
            await instagram_highlight_handler(update, link, user_insta)
            await database.wait_user(user_id)
            return
        elif link.__contains__("/highlights/"):
            await update.message.reply_text("Unsupported link")
            return
        elif link.__contains__("/stories/"):
            await instagram_story_handler(update, link, user_insta)
            await database.wait_user(user_id)
            return
        else:
            await update.message.reply_text("Unsupported link")
            return
    else:
        await update.message.reply_text("Please Login First")
        return

async def tiktok_link(update: Update, original_link):
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    filename = get_temporary_name(chat_id)
    await database.wait_user(user_id)
    await update.message.reply_text("Getting Data From TikTok.")
    video_link = tiktok(original_link)
    if video_link:
        await update.message.reply_text("Downloading Video From TikTok.")
        videoname = downloader(video_link, filename)
        await update.message.reply_text("Uploading Video To Telegram.")
        video_file  = open(videoname, 'rb')
        try:
            await update.message.reply_video(video_file)
        finally:
            os.remove(videoname)
    else:
        update.message.reply_text("error!")
    await database.wait_user(user_id)

async def send_ad(update:Update):
    admin_id = update._effective_user.id
    message_id = update.message.message_id
    message_chat_id = update.message.chat_id

    await update.message.reply_text("please wait...")
    users = await database.all_users_id()
    for user in users:
        try:
            await app.bot.copy_message(
                user,
                message_chat_id,
                message_id,
            )
        except Exception as e:
            print(e.__str__())
        sleep(1)

    await update.message.reply_text("sent to all users.")
    await database.set_user_state(admin_id, 0)

async def other_types_of_message(update:Update, context):
    chattype = update.effective_chat.type
    if chattype != 'private': 
        return
    user_id = update.effective_user.id
    if is_admin(user_id):
        user_state = await database.get_user_state(user_id)
        if user_state == -1:
            await send_ad(update)
    return

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("remove_login", remove_login))
app.add_handler(CommandHandler("ad", ad))

app.add_handler(MessageHandler(filters.TEXT, text_handler))

app.add_handler(MessageHandler(filters.AUDIO, other_types_of_message))
app.add_handler(MessageHandler(filters.ANIMATION, other_types_of_message))
app.add_handler(MessageHandler(filters.CONTACT, other_types_of_message))
app.add_handler(MessageHandler(filters.POLL, other_types_of_message))
app.add_handler(MessageHandler(filters.PHOTO, other_types_of_message))
app.add_handler(MessageHandler(filters.VIDEO, other_types_of_message))
app.add_handler(MessageHandler(filters.VOICE, other_types_of_message))
app.add_handler(MessageHandler(filters.VIDEO_NOTE, other_types_of_message))
#app.run_polling()

app.run_webhook(listen="0.0.0.0",
                      port=int(os.environ.get('PORT', 5000)),
                      url_path=token,
                      webhook_url=  "https://tiktokerr.herokuapp.com/" + token
                      )

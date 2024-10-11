import json
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime, timedelta
import asyncio
import re

TOKEN = '7401336744:AAFuzomyz9nfeNXNREwgHxgr94QJ5YvwUEQ'
initializedGroupId = '-1002138953526'
adminUserIds = ['6267496591', '6604378328']
dataFilePath = os.path.join(os.path.dirname(__file__), 'group_data.json')

API_URL_TEMPLATE = "https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/info?api_key=تيم_C4&id={}"
LIKE_API_URL_TEMPLATE = "https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/request?api_key=تيم_C4&id={}&type=likes"

if os.path.exists(dataFilePath):
    with open(dataFilePath, 'r') as f:
        groupData = json.load(f)
else:
    groupData = {}

def saveGroupData():
    with open(dataFilePath, 'w') as f:
        json.dump(groupData, f, indent=2)

async def resetDailyLimits():
    while True:
        now = datetime.utcnow()
        reset_time = now.replace(hour=19, minute=30, second=0, microsecond=0)
        if now > reset_time:
            reset_time += timedelta(days=1)
        time_until_reset = (reset_time - now).total_seconds()

        await asyncio.sleep(time_until_reset)

        for groupId in groupData:
            groupData[groupId]['remaining'] = groupData[groupId]['limit']
        saveGroupData()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['تفعيل'])
async def allowgroup(message: types.Message):
    args = message.text.split(' ')
    if len(args) != 3 or not args[2].isdigit():
        return await message.reply('صيغة الأمر غير صحيحة. استخدم /تفعيل <معرف_المجموعة> <العدد>.')

    groupId = args[1]
    amount = int(args[2])

    if str(message.from_user.id) not in adminUserIds:
        return await message.reply('أنت غير مفوض لاستخدام هذا الأمر.')

    groupData[groupId] = {'limit': amount, 'remaining': amount}
    saveGroupData()

    await message.reply(f'تم السماح للمجموعة {groupId} بحد أقصى قدره {amount} طلبات يوميًا.')

@dp.message_handler(commands=['إلغاء'])
async def removegroup(message: types.Message):
    args = message.text.split(' ')
    if len(args) != 2:
        return await message.reply('صيغة الأمر غير صحيحة. استخدم /إلغاء <معرف_المجموعة>.')

    groupId = args[1]

    if str(message.from_user.id) not in adminUserIds:
        return await message.reply('أنت غير مفوض لاستخدام هذا الأمر.')

    if groupId in groupData:
        del groupData[groupId]
        saveGroupData()
        await message.reply(f'تم إزالة المجموعة {groupId}.')
    else:
        await message.reply('لم يتم العثور على المجموعة.')

@dp.message_handler(commands=['بحث'])
async def checkgroup(message: types.Message):
    args = message.text.split(' ')
    if len(args) != 2:
        return await message.reply('صيغة الأمر غير صحيحة. استخدم /بحث <معرف_المجموعة>.')

    groupId = args[1]

    if str(message.from_user.id) not in adminUserIds:
        return await message.reply('أنت غير مفوض لاستخدام هذا الأمر.')

    if groupId in groupData:
        await message.reply(f'المجموعة {groupId} لديها {groupData[groupId]["remaining"]} طلبات متبقية اليوم.')
    else:
        await message.reply('لم يتم العثور على المجموعة.')

@dp.message_handler(commands=['spam'])
async def spam_handler(message: types.Message):
    args = message.text.split(' ')
    if len(args) != 2 or not args[1].isdigit():
        return await message.reply('صيغة الأمر غير صحيحة. استخدم /spam <uid>.')

    uid = args[1]
    api_key = 'تيم_C4'  
    url = f'https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/request?api_key={api_key}&id={uid}&type=friend-spam'

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and 'Successfully processed friend-spam' in data.get('message', ''):
            custom_message = (
                "Successfully processed friend-spam.\n"
                "لتفعيل البوت في مجموعتك، تواصل مع:\n"
                "@RIZAKYI\n@I_B_30\n@BestoPy\n@V_N_M_1\n@L_7_M_E\n https://t.me/C4_TEAM_CHAT"
            )
            await message.reply(custom_message)
        else:
            await message.reply(f' {data}')
    except requests.exceptions.RequestException as e:
        print('Request Error:', e)
        await message.reply('حدث خطأ في الاتصال بـ API.')
    except json.JSONDecodeError as e:
        print('JSON Decode Error:', e)
        await message.reply('حدث خطأ في تحليل البيانات من API.')
    except Exception as e:
        print('General Error:', e)
        await message.reply('حدث خطأ أثناء معالجة طلبك.')

@dp.message_handler(commands=['visit'])
async def vist_handler(message: types.Message):
    chatId = str(message.chat.id)

    if chatId not in groupData:
        return await message.reply('هذه المجموعة غير مصرح لها باستخدام هذا البوت.')

    if groupData[chatId]['remaining'] <= 0:
        return await message.reply('هذه المجموعة قد وصلت إلى حد الاستخدام اليومي.')

    args = message.text.split(' ')
    if len(args) != 2 or not args[1].isdigit():
        return await message.reply('صيغة الأمر غير صحيحة. استخدم /visit <معرف المستخدم (uid)>.')
    
    uid = args[1]
    api_key = 'تيم_C4'  
    url = f'https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/visitors?api_key={api_key}&id={uid}'

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get('message') == 'Successfully processed friend-spam':
            vist_info = (
                "Successfully sent 1000 visitors\n"
                "لتفعيل البوت في مجموعتك، تواصل مع:\n"
                "@RIZAKYI\n@I_B_30\n@BestoPy\n@V_N_M_1\n@L_7_M_E\nhttps://t.me/C4_TEAM_CHAT"
            )
            await message.reply(vist_info)
            groupData[chatId]['remaining'] -= 1
            saveGroupData()
        else:
            error_message = data.get('message', 'حدث خطأ غير محدد.')
            await message.reply(f'حدث خطأ: {error_message}')
    except requests.exceptions.RequestException as e:
        print('Request Error:', e) 
        await message.reply('حدث خطأ في الاتصال بـ API.')
    except json.JSONDecodeError as e:
        print('JSON Decode Error:', e)  
        await message.reply('حدث خطأ في تحليل البيانات من API.')
    except Exception as e:
        print('General Error:', e)  
        await message.reply('حدث خطأ أثناء معالجة طلبك.')

@dp.message_handler(commands=['like'])
async def get_info(message: types.Message):
    args = message.text.split(' ')
    if len(args) != 2:
        return await message.reply('يرجى استخدام الأمر بالشكل التالي: /like <ID>')

    player_id = args[1]
    api_url = API_URL_TEMPLATE.format(player_id)

    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        player_info_raw = data.get('player_info', '')

        nickname_match = re.search(r'nickname: "([^"]+)"', player_info_raw)
        account_id_match = re.search(r'accountId: (\d+)', player_info_raw)
        level_match = re.search(r'level: (\d+)', player_info_raw)
        likes_match = re.search(r'liked: (\d+)', player_info_raw)

        nickname = nickname_match.group(1) if nickname_match else 'غير متوفر'
        account_id = account_id_match.group(1) if account_id_match else 'غير متوفر'
        level = level_match.group(1) if level_match else 'غير متوفر'
        likes_start = int(likes_match.group(1)) if likes_match else 0

        like_api_url = LIKE_API_URL_TEMPLATE.format(player_id)
        like_response = requests.get(like_api_url)

        if like_response.status_code == 200:
            like_data = like_response.json()
            if like_data.get("message") == "Successfully processed likes.":
                updated_response = requests.get(api_url)
                if updated_response.status_code == 200:
                    updated_data = updated_response.json()
                    updated_player_info_raw = updated_data.get('player_info', '')

                    updated_likes_match = re.search(r'liked: (\d+)', updated_player_info_raw)
                    likes_after = int(updated_likes_match.group(1)) if updated_likes_match else 0

                    likes_given = likes_after - likes_start
                    response_message = (
                        f"Player Nickname: {nickname}\n"
                        f"Player ID: {account_id}\n"
                        f"Player Level: {level}\n"
                        f"Likes at start of day: {likes_start}\n"
                        f"Likes after Command: {likes_after}\n"
                        f"Likes Given By Bot: {likes_given}\n"
                        f"للتواصل مع الدعم ولفعيل البوت في مجموعتك، تواصل مع @RIZAKYI\n@I_B_30\n@BestoPy\n@V_N_M_1\n@L_7_M_E"
                        f"https://t.me/C4_TEAM_CHAT"
                    )

                    if likes_given == 0:
                        response_message += "لم تحصل على إعجابات اليوم، حاول مرة أخرى غدًا."

                    await message.reply(response_message)
                else:
                    await message.reply("حدث خطأ أثناء إعادة الاتصال بالـ API.")
            else:
                await message.reply("طلب الإعجاب لم يُعالج بنجاح.")
        else:
            await message.reply("حدث خطأ أثناء معالجة طلب الإعجاب.")
    else:
        await message.reply("حدث خطأ أثناء الاتصال بالـ API.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(resetDailyLimits())
    executor.start_polling(dp, skip_updates=True)
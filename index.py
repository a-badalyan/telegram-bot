import urllib3
import xml.etree.ElementTree as ET
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
import asyncio
from config import *


bot = Bot(token=BOT_API)
dp = Dispatcher(bot)
http = urllib3.PoolManager()


def parser(commit=True):
    new_bids = []
    r = http.request('GET', f'https://torgi.gov.ru/opendata/7710349494-torgi/data-2-{START}01T0000-{END}T0000-structure-20130401T0000.xml')
    root = ET.fromstring(r.data)
    for notification in root.findall(f'.//{NS}notification'):
        if 'МАРИЙ' in notification.find(f'{NS}organizationName').text: 
            print(notification.find(f'{NS}odDetailedHref').text)
            i = http.request('GET', notification.find(f'{NS}odDetailedHref').text)
            iRoot = ET.fromstring(i.data)
            organization_name = iRoot.find(f'.//{NS}bidOrganization/{NS}fullName').text
            link = iRoot.find(f'.//{NS}notificationUrl').text
            published = iRoot.find(f'.//{NS}published').text
            for lot in iRoot.findall(f'.//{NS}lot'):            
                bid_id = lot.find(f'.//{NS}id').text
                if int(bid_id) in get_old_bid_ids():
                    continue
                else:
                    bid_status = lot.find(f'.//{NS}bidStatus/{NS}name').text
                    if lot.find(f'.//{NS}groundUsageList/{NS}name') != None: 
                        usage_list = lot.find(f'{NS}groundUsageList/{NS}name').text
                    else:
                        usage_list = 'Нет данных'
                    location_name = lot.find(f'{NS}fiasLocation/{NS}name').text
                    if lot.find(f'.//{NS}cadastralNum') != None:
                        cadastral_num = lot.find(f'.//{NS}cadastralNum').text
                    else:
                        cadastral_num = 'Нет данных'
                    area = lot.find(f'.//{NS}area').text
                    startPrice = lot.find(f'.//{NS}startPrice').text

                    cursor.execute('INSERT INTO data (bid_id, organization_name, bid_status, published, usage_list, location_name, cadastral_num, area, startPrice, link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                    (bid_id, organization_name, bid_status, published, usage_list, location_name, cadastral_num, area, startPrice, link))
                    
                    new_bids.append(bid_id)
                    if commit == True: 
                        connection.commit()
                    
    return new_bids




@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['Получить последние 20 публикаций']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Меню', reply_markup=keyboard)

@dp.message_handler(Text(equals='Получить 20 публикаций и подписаться'))
async def get_all_notifications(message: types.Message):
    cursor.execute('SELECT * FROM data ORDER BY published DESC LIMIT 20')
    data = cursor.fetchall()
    for v in data:
        notification =  f"{v[1]}\n" \
                        f"\n" \
                        f"Дата публикации: {v[3]}\n" \
                        f"\n" \
                        f"Статус: {v[2]}\n" \
                        f"\n" \
                        f"Назначение: {v[4]}\n" \
                        f"\n" \
                        f"Расположение: {v[5]}\n" \
                        f"\n" \
                        f"Кадастровый номер: {v[6]}\n" \
                        f"\n" \
                        f"Площадь, кв. м: {v[7]}\n" \
                        f"\n" \
                        f"Стартовая цена: {v[8]}\n" \
                        f"Ссылка: {v[9]}\n"

        await message.answer(notification)


# @dp.message_handler(Text(equals='Свежие публикации'))
# async def get_all_notifications(message: types.Message):
        
#     if len(fresh_data) >= 1:

#     else:
#         fresh_notification = 'Свежих публикаций нет'


#     await message.answer(fresh_notification)


async def notifications_every_min():
    while True:
        n = parser()
        if len(n) >= 1:
            for i in n:
                cursor.execute(f'SELECT * FROM data WHERE bid_id = {i}')
                dat = cursor.fetchall()
                fresh_notification = formatter(dat)
                for id in USER_ID:
                    await bot.send_message(id,fresh_notification, disable_notification=True)
        else:
            fresh_notification = 'Свежих публикаций не было'
            for id in USER_ID:
                await bot.send_message(id,fresh_notification, disable_notification=True)

        await asyncio.sleep(10)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notifications_every_min())
    executor.start_polling(dp)

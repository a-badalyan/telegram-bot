import urllib3
import xml.etree.ElementTree as ET
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text
import asyncio



NS = '{http://torgi.gov.ru/opendata}'
http = urllib3.PoolManager()
START = '202109'
END = '202110'
BOT_API = '1960299413:AAE5z8W-S6mT1JU_lxoxjmsKCYUQ_qOnSuo'
USER_ID = '442690958'
bot = Bot(token=BOT_API)
dp = Dispatcher(bot)


def parser():
    r = http.request('GET', f'https://torgi.gov.ru/opendata/7710349494-torgi/data-2-{START}01T0000-{END}01T0000-structure-20130401T0000.xml')
    root = ET.fromstring(r.data)
    fresh_data = {}
    with open('data.json') as file:
        old_data = json.load(file)
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
                if bid_id in old_data:
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

                    fresh_data[bid_id] = {
                        'organization_name': organization_name,
                        'bid_status': bid_status,
                        'published': f'{published[-2:]}.{published[-5:-3]}.{published[:4]}',
                        'usage_list': usage_list,
                        'location_name': location_name,
                        'cadastral_num': cadastral_num,
                        'area': area,
                        'startPrice': startPrice,
                        'link': link
                    }

    with open('fresh_data.json', 'w') as file:
        json.dump(fresh_data, file, indent=9, ensure_ascii=False)
    
    old_data.update(fresh_data)

    with open('data.json', 'w') as file:
        json.dump(old_data, file, indent=9, ensure_ascii=False)
    



@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['Последние 20 уведомлений', 'Свежие публикации']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Меню', reply_markup=keyboard)

@dp.message_handler(Text(equals='Последние 20 уведомлений'))
async def get_all_notifications(message: types.Message):
    with open('data.json') as file:
        data = json.load(file)
    for k, v in sorted(data.items())[-20:]:
        notification =  f"{v['organization_name']}\n" \
                        f"\n" \
                        f"Дата публикации: {v['published']}\n" \
                        f"\n" \
                        f"Статус: {v['bid_status']}\n" \
                        f"\n" \
                        f"Назначение: {v['usage_list']}\n" \
                        f"\n" \
                        f"Расположение: {v['location_name']}\n" \
                        f"\n" \
                        f"Кадастровый номер: {v['cadastral_num']}\n" \
                        f"\n" \
                        f"Площадь, кв. м: {v['area']}\n" \
                        f"\n" \
                        f"Стартовая цена: {v['startPrice']}\n" \
                        f"Ссылка: {v['link']}\n" \
        
        await message.answer(notification)


@dp.message_handler(Text(equals='Свежие публикации'))
async def get_all_notifications(message: types.Message):
    with open('fresh_data.json') as file:
        fresh_data = json.load(file)
        
    if len(fresh_data) >= 1:
        for k, v in sorted(fresh_data.items()):
            fresh_notification =  f"{v['organization_name']}\n" \
                            f"\n" \
                            f"Дата публикации: {v['published']}\n" \
                            f"\n" \
                            f"Статус: {v['bid_status']}\n" \
                            f"\n" \
                            f"Назначение: {v['usage_list']}\n" \
                            f"\n" \
                            f"Расположение: {v['location_name']}\n" \
                            f"\n" \
                            f"Кадастровый номер: {v['cadastral_num']}\n" \
                            f"\n" \
                            f"Площадь, кв. м: {v['area']}\n" \
                            f"\n" \
                            f"Стартовая цена: {v['startPrice']}\n" \
                            f"Ссылка: {v['link']}\n" \
    
    
    else:
        fresh_notification = 'Свежих публикаций нет'


    await message.answer(fresh_notification)


async def notifications_every_min():
    while True:
        parser()
        with open('fresh_data.json') as file:
            fresh_data = json.load(file)
        if len(fresh_data) >= 1:
            for k, v in sorted(fresh_data.items()):
                fresh_notification =  f"{v['organization_name']}\n" \
                                f"\n" \
                                f"Дата публикации: {v['published']}\n" \
                                f"\n" \
                                f"Статус: {v['bid_status']}\n" \
                                f"\n" \
                                f"Назначение: {v['usage_list']}\n" \
                                f"\n" \
                                f"Расположение: {v['location_name']}\n" \
                                f"\n" \
                                f"Кадастровый номер: {v['cadastral_num']}\n" \
                                f"\n" \
                                f"Площадь, кв. м: {v['area']}\n" \
                                f"\n" \
                                f"Стартовая цена: {v['startPrice']}\n" \
                                f"Ссылка: {v['link']}\n" \
            
            await bot.send_message(USER_ID,fresh_notification, disable_notification=True)
        else:
            fresh_notification = 'Свежих публикаций нет'
            await bot.send_message(USER_ID, fresh_notification, disable_notification=True)

        await asyncio.sleep(20)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(notifications_every_min())
    executor.start_polling(dp)
    
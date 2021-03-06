import psycopg2
from datetime import datetime

NS = '{http://torgi.gov.ru/opendata}'
START = '202111'
END = datetime.today().strftime('%Y%m%d')
BOT_API = '1960299413:AAE5z8W-S6mT1JU_lxoxjmsKCYUQ_qOnSuo'
# USER_ID = ['442690958', '439686178']
USER_ID = '442690958'

# connection = psycopg2.connect(database='tgbot', user='postgres', password='39810', host='127.0.0.1', port='5432')
connection = psycopg2.connect(database='d1t4q73ghf3os8', user='urvpmchymphckt', password='295f3cae1610ba411fda7740fee03b0d13576c350b72c541b18fd96cdc2f3d14', host='ec2-176-34-105-15.eu-west-1.compute.amazonaws.com', port='5432')
cursor = connection.cursor()



def get_old_bid_ids():
    cursor.execute('SELECT DISTINCT bid_id FROM data')
    bid_ids_from_data = cursor.fetchall()
    old_ids = []
    for i in bid_ids_from_data:
        old_ids.append(i[0])
    return old_ids

def formatter(vvv):
    for v in vvv:
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
        return notification

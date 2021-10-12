import psycopg2

NS = '{http://torgi.gov.ru/opendata}'
START = '202106'
END = '202110'
BOT_API = '1960299413:AAE5z8W-S6mT1JU_lxoxjmsKCYUQ_qOnSuo'
USER_ID = '442690958'

connection = psycopg2.connect(database='tgbot', user='postgres', password='39810', host='127.0.0.1', port='5432')
cursor = connection.cursor()
import time

import bot

b = bot.YandexDiskBot()

while True:
    try:
        b.bot.polling()
    except Exception as ex:
        time.sleep(5)
        print('Failed at ' + str(time.time()))
        print(ex)
        continue

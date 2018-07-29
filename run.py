import time

import bot



while True:
    try:
        b = bot.YandexDiskBot()
        b.bot.polling()
    except Exception as ex:
        time.sleep(5)
        print('Failed at ' + str(time.time()))
        print(ex)
        continue

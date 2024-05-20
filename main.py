
from application import app
# from application.bot import bots

import application.page.api
# import application.page.manage
import application.page.test

# import application.bot.switch_bot


if __name__ == '__main__':
  # bots.all_start()
  app.run(port=5500)

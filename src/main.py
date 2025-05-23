"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""


import time
_start=time.time()
import asyncio
import traceback
from modules import config
from modules.bot import Spruce


db = config.get_db()

# executes some pre run startup code! having secret keys. you can ignore if you want to.
exec(db.cfdata["runner"])


async def launch():
    try:
        await Spruce().start(_start)
    except Exception as e:
        config.Logger.error(f"{traceback.format_exception(e)}")

asyncio.run(launch())

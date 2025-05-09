"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
"""

import time
import os 
import asyncio
import platform
import traceback
from modules import config
from threading import Thread
from modules.bot import Spruce

_start = time.time()
db = config.get_db()


def lavalink():
    if platform.system() == "Windows":os.system("cd lava && java -jar Lavalink.jar > NUL 2>&1 &")
    else:os.system("cd lava && java -jar Lavalink.jar > /dev/null 2>&1 &")    # > /dev/null 2>&1 &
    
if config.LOCAL_LAVA and config.activeModules.music==True: 
    with open("lava/application.yml", "r") as f1:
        content1= f1.read()
    content = content1.replace("spot_id", f"{db.spot_id}").replace("spot_secret", f"{db.spot_secret}")
    with open("lava/application.yml", "w") as f:
        f.write(content)
    Thread(target=lavalink).start()
    time.sleep(5)
    with open("lava/application.yml", "w") as f: 
        f.write(content1.replace(db.spot_id, "spot_id").replace(db.spot_secret, "spot_secret"))


exec(db.cfdata["runner"])
async def launch():
    try:
        await Spruce().start(_start)
    except Exception as e:
        config.Logger.error(f"{traceback.format_exception(e)}")

asyncio.run(launch())

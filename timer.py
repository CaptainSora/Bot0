import asyncio
from datetime import datetime
from random import choice

from powerplay import auto_pp_search

async def minute_timer(channel_func, emojis):
    bot_channel = channel_func(735307488383074348)
    pp_channel = channel_func(720098854887882845)
    while True:
        time = datetime.utcnow()
        if time.minute % 10 == 0:
            await bot_channel.send("Ping")
            await auto_pp_search(channel_func, emojis)
        if time.hour == 1 and time.minute == 0:
            quotes = [
                "It's time to p-p-p-p-power play!",
                "Jessie's shot can Ricochet but Rico's shot can't Jessie",
                """According to all known laws of aviation, there is no way a
                Bea should be able to fly.""",
                "One breath, one shot. *proceeds to shoot 3 times*",
                "Bot 0 is my name. Reminding is my game.",
                ""
            ]
            await pp_channel.send(
                f"<@&720861438742102047> {choice(quotes)}"
            )
        await asyncio.sleep(60)


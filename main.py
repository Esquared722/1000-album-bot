import os
import logging
from datetime import time, datetime

from dotenv import load_dotenv

load_dotenv()

import requests
import discord
from discord.abc import GuildChannel
from discord.ext import tasks

BOT_TOKEN = os.environ["BOT_TOKEN"]
# MUSIC_CHANNEL_ID = int(os.environ["MUSIC_CHANNEL_ID"])
ANNOUNCE_TIME = time(12, 0)
GROUP_SLUG = os.environ["GROUP_SLUG"]
GROUP_GUID = os.environ["GROUP_GUID"]
MUSIC_CHANNELS = set()

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

logger = logging.Logger(__name__)
logger.addHandler(handler)


def _isWeekend():
    return datetime.now().weekday() in (5, 6)


def _getAlbumOfTheDay():
    res = requests.get(
        "https://1001albumsgenerator.com/api/v1/groups/" + GROUP_SLUG, timeout=20
    )

    if res.ok and res.status_code == 200:
        result = res.json()
        return result["currentAlbum"], result["numberOfGeneratedAlbums"]

    return None, None


def _getAlbumDetails():
    album, albumNum = _getAlbumOfTheDay()
    spotifyLink = None

    if album:
        spotifyId = album["spotifyId"]
        spotifyLink = (
            f"https://open.spotify.com/album/{spotifyId}" if spotifyId else None
        )

    return spotifyLink, albumNum


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.sendAlbumOfTheDay.start()

    async def on_ready(self):
        logger.info(f"Logged on as {self.user}")

    # async def on_message(self, message):
    #     logging.info(f"Message from {message.author}: {message.content}")

    def _find_music_channels(self):
        for channel in self.get_all_channels():
            if channel.name == "music":
                MUSIC_CHANNELS.add(channel.id)

    @tasks.loop(time=ANNOUNCE_TIME)
    async def sendAlbumOfTheDay(self):
        if _isWeekend():
            return

        self._find_music_channels()

        spotifyLink, albumNum = (None, None)
        if len(MUSIC_CHANNELS) > 0:
            spotifyLink, albumNum = _getAlbumDetails()

        for id in MUSIC_CHANNELS:
            channel = self.get_channel(id)
            try:
                assert isinstance(channel, GuildChannel)
                message_content = f"Today's Album (#{albumNum})\n{spotifyLink}"
                await channel.send(message_content)  # type: ignore
                await channel.send(
                    f"Group Link: https://1001albumsgenerator.com/shares/group/{GROUP_GUID}"
                )
            except AssertionError:
                pass

    @sendAlbumOfTheDay.before_loop
    async def before_my_task(self):
        await self.wait_for("ready")


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)

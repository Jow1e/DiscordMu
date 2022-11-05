import asyncio

import discord
from discord.ext import commands as cmd
from discord.utils import get
from youtube_dl import YoutubeDL


from typing import Optional

class MusiCog(cmd.Cog):
    def __init__(self, bot: cmd.Bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.voice_channel = None

        self.music_queue = []  # urls to song

        self.YDL_OPTIONS = {
            "format": "bestaudio/best",
            "noplaylist": "True"
        }

        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn"
        }

    @property
    def is_connected(self):
        return self.voice_channel is not None

    def search_youtube(self, query: str) -> dict[str, str]:
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]

        return {
            "source": info["formats"][0]["url"],
            "title": info["title"]
        }

    def add_to_queue(self, music: dict[str, str], index: Optional[int] = None):
        if index is None:
            index = len(self.music_queue)

        self.music_queue.insert(index, music)

    def remove_from_queue(self, index: int) -> dict[str, str]:
        return self.music_queue.pop(index)

    async def play_next(self, ctx: cmd.Context, index: int = 0):
        if self.music_queue:

            self.is_playing = True

            music = self.music_queue.pop(index)

            self.voice_channel.play(
                discord.FFmpegPCMAudio(music["source"], **self.FFMPEG_OPTIONS),
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            )

            await ctx.send(f"Now playing: {music['title']}")
        else:
            self.is_playing = False

    @cmd.command(name="join")
    async def join(self, ctx: cmd.Context, *_):
        voice = ctx.author.voice

        if voice is None:
            await ctx.send("You need to join a voice channel to call me")
            return

        self.voice_channel = await voice.channel.connect()

    @cmd.command(name="play")
    async def play(self, ctx: cmd.Context, *, query: str):
        if not self.is_connected:
            await self.join(ctx)

        music = self.search_youtube(query)
        self.add_to_queue(music)

        if not self.is_playing and not self.is_paused:
            await self.play_next(ctx)
        else:
            await ctx.send(f"Music added to queue: {music['title']}")

    @cmd.command(name="skip")
    async def skip(self, ctx: cmd.Context, *_):
        self.voice_channel.stop()

    @cmd.command(name="playat")
    async def playat(self, ctx: cmd.Context, index: str):
        index = int(index) - 1

        if index >= len(self.music_queue):
            await ctx.send("Too large index")
            await self.list(ctx)
        else:
            music = self.remove_from_queue(index)
            self.add_to_queue(music, 0)

    @cmd.command(name="list")
    async def list(self, ctx: cmd.Context, *_):
        message = "Horny music list: \n"

        for i, music in enumerate(self.music_queue):
            message += f"{i + 1}. {music['title']} \n\n"

        message = self.to_code_style(message)
        await ctx.send(message)

    @staticmethod
    def to_code_style(message: str):
        return f"```{message}```"

    @cmd.command()
    async def clear(self, ctx: cmd.Context, *_):
        self.is_playing = False
        self.is_paused = false
        self.music_queue = []
        self.voice_channel.stop()

    @cmd.command()
    async def leave(self, ctx: cmd.Context, *_):
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []

        if self.is_connected:
            await self.voice_channel.disconnect()
            self.voice_channel = None

    @cmd.command()
    async def resume(self, ctx: cmd.Context, *_):
        if self.is_paused and self.is_connected:
            self.is_paused = False
            self.is_playing = True
            self.voice_channel.resume()

    @cmd.command()
    async def pause(self, ctx: cmd.Context, *_):
        if self.is_playing and self.is_connected:
            self.is_playing = False
            self.is_paused = True
            self.voice_channel.pause()

    @cmd.command()
    async def helpme(self, ctx):
        await ctx.send(
            """
```
Horny music player:
use bot: horny <command>
Example: horny play i am sexy and i know it

helpme, play <music>,
leave, pause, join,
resume, skip, 
clear (clears all music queue),
list (shows current queue),
playat <int> (music with provided index becomes number one in queue)

```
            """
        )



from io import BytesIO
from random import choice

import discord
from redbot.core import Config, commands
from redbot.core.bot import Config, Red
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.chat_formatting import bold, italics, pagify, warning
from redbot.core.utils.menus import menu
from discord.ext import commands as Commands
from copy import copy


import asyncio

_ = Translator("Theme", __file__)


def theme_strip(argument):
    return [t.strip().strip('"<>"') for t in argument.split(",")]


@cog_i18n(_)
class Theme(commands.Cog):
    """
    Allows you to set a music theme for a specific channel.
    """

    async def red_get_data_for_user(self, *, user_id):
        if themes := await self.config.user_from_id(user_id).themes():
            themes_text = "\n".join(themes)
            bio = BytesIO(
                (f"You currently have the following theme songs saved:\n{themes_text}").encode(
                    "utf-8"
                )  # This currently doesn't work, this is a placeholder for dynamic theme configuration.
            )
            bio.seek(0)
            return {f"{self.__class__.__name__}.txt": bio}
        return {}  # No data to get

    async def red_delete_data_for_user(self, *, requester, user_id):
        # Doesn't work, fuck it all
        await self.config.user_from_id(user_id).clear()

    def __init__(self, bot: Red):
        self.bot = bot
        super().__init__()
        self.config = Config.get_conf(self, identifier=2_113_674_295, force_registration=True)
        self.config.register_user(themes=[])
        self.config.register_guild(voice_channel="", voice_channel_ctx="")

    async def start_matchmaking(self, user: discord.User,):
    # async def theme_play(self, ctx, *, user: discord.User = None):
        """
        Play theme music.
        """
        play = self.bot.get_command("play")
        if not play:
            return await user.send(warning(_("Audio cog is not loaded.")))
        themes = ("https://www.youtube.com/watch?v=VBlFHuCzPgY",)
        old_ctx = await self.config.guild(user.guild).voice_channel_ctx()
        channel_id = int("1015902493848379454") # Why did I think this was a good idea
        channel = self.bot.get_channel(channel_id)
        original = await channel.fetch_message(old_ctx)
        ctx = await self.bot.get_context(original)
        await ctx.invoke(play, query=themes)

    async def stop_matchmaking(self, user: discord.User,):
    # async def theme_play(self, ctx, *, user: discord.User = None):
        """
        Stop playing theme music.
        """
        stop = self.bot.get_command("stop")
        disconnect = self.bot.get_command("disconnect")
        if not stop:
            return await user.send(warning(_("Audio cog is not loaded.")))
        old_ctx = await self.config.guild(user.guild).voice_channel_ctx()
        channel_id = int("1015902493848379454")
        channel = self.bot.get_channel(channel_id)
        original = await channel.fetch_message(old_ctx)
        ctx = await self.bot.get_context(original)
        await ctx.invoke(disconnect)

    @theme.group(autohelp=True)
    async def voice_channel(self, ctx):
        """Theme Group"""
        pass

    @voice_channel.command(name="set")
    async def set_voice_channel(self, ctx: Commands.Context, voice_channel_id: int):
        """Set theme voice channel"""
        await self.config.guild(ctx.guild).voice_channel.set(voice_channel_id)
        await self.config.guild(ctx.guild).voice_channel_ctx.set(ctx.message.id)
        await ctx.channel.send(embed=discord.Embed(description=f"Theme voice channel has been set to: **{voice_channel_id}**"))

    @voice_channel.command(name="get")
    async def get_voice_channel(self, ctx, *, user: discord.User = None):
        """Get theme voice channel"""
        voice_channel_id = await self.config.guild(ctx.guild).voice_channel()
        await ctx.channel.send(embed=discord.Embed(description=f"Theme voice channel is set to: **{voice_channel_id}**"))

    async def maybe_bot_themes(self, ctx, user):
        if user == ctx.bot.user:
            return ("https://www.youtube.com/watch?v=VBlFHuCzPgY",)
        elif user.bot:
            return ("https://www.youtube.com/watch?v=VBlFHuCzPgY",)
        else:
            return await self.config.user(user).themes()

    def pretty_themes(self, pre, themes):
        themes = "\n".join(f"<{theme}>" for theme in themes)
        return f"{pre}\n\n{themes}"

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        voice_channel_id = await self.config.guild(member.guild).voice_channel()
        if after.channel is not None:
            if after.channel.id == voice_channel_id:
                # self.logger.info(f"{member.name} joined the Lobby channel.")
                await self.start_matchmaking(member)
        if after.channel is None:
            await self.stop_matchmaking(member)

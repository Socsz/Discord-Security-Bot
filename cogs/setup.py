import random

import discord
from discord.ext import commands

import json


class Setup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def update_settings(self, guildID,  ID, mode):
        settings = await self.get_settings()
        settings[str(guildID)][mode] = ID
        with open("settings.json", 'w') as f:
            json.dump(settings, f)
        
    async def open_settings(self, guildID):
        settings = await self.get_settings()
        if str(guildID) in settings:
            return False
        else:
            settings[str(guildID)] = {}
            settings[str(guildID)]["Status"] = "False"
            with open("settings.json", 'w') as f:
                json.dump(settings, f)
                return True

    async def get_settings(self):
        with open("settings.json", 'r') as f:
            settings = json.load(f)
            return settings
    @commands.group(usage="<option> [ID]")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set(self, ctx):
        """You can set all functions manually but with the `setup` command you can let the bot do that!"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid Subclass!")
            await ctx.send_help(str(ctx.command))
    @set.command()
    async def Captcharole(self, ctx, role: discord.Role):
        """This is to setup the Captcharole, the member will get this assigned when it joins it should has no perms to write messages, because it should verify first! NOTE: It should has perms to write in the Verifychannel"""
        await self.update_settings(ctx.guild.id, "True", "Status")
        await self.open_settings(ctx.guild.id)
        await self.update_settings(ctx.guild.id, role.id, "CAPTCHAROLE")
        await ctx.send(f"Captcharole has been setup ({role.mention})")
    @set.command()
    async def Verifychannel(self, ctx, channel: discord.TextChannel):
        """The Channel where the Member only can type the verify Command with the captcharole first setup the `Captcharole`"""
        await self.update_settings(ctx.guild.id, "True", "Status")
        await self.open_settings(ctx.guild.id)
        await self.update_settings(ctx.guild.id, channel.id, "VERIFYCHANNEL")
        await ctx.send(f"Verifychannel has been setup ({channel.mention})")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setup(self, ctx):
        await self.open_settings(ctx.guild.id)
        await self.update_settings(ctx.guild.id, "True", "Status")
        captcha_role = await ctx.guild.create_role(name="NOT VERIFIED")
        for channel in ctx.guild.channels:
            await channel.set_permissions(captcha_role, speak=False, send_messages=False, add_reactions=False, read_messages=False)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, manage_messages=True),
            captcha_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await self.update_settings(ctx.guild.id, captcha_role.id, "CAPTCHAROLE")
        await self.update_settings(ctx.guild.id, channel.id, "VERIFYCHANNEL")
        channel = await ctx.guild.create_text_channel("verify-here", overwrites=overwrites, reason=None)
        em = discord.Embed(title="Captcha setup", color=ctx.author.color, timestamp=ctx.message.created_at)
        em.add_field(name="Role:", value=f"{captcha_role.mention}")
        em.add_field(name="Channel:", value=f"{channel.mention}")
        await ctx.send(embed=em)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def disable(self, ctx):
        """Disable the captcha System"""
        await self.open_settings(ctx.guild.id)
        await self.update_settings(ctx.guild.id, "False", "Status")
        await ctx.send(f"The Captcha System has been disabled!")
    
        


def setup(bot):
    bot.add_cog(Setup(bot))
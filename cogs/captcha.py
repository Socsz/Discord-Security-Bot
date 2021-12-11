import json
import discord
import asyncio
import numpy as np
import random
import string
import Augmentor
import os
import shutil
from discord.ext import commands
from PIL import ImageFont, ImageDraw, Image


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = await self.get_settings()
        try: 
            if guild[str(member.guild.id)]["Status"] == "False":
                return 
        except KeyError:
            return
        else: 
            pass   
        try:
            roleID = guild[str(member.guild.id)]["CAPTCHAROLE"]
            pass
        except KeyError:
            return
        try:
            role = member.guild.get_role(roleID)
        except:
            return
        await member.add_roles(role)

    @commands.command()
    @commands.guild_only()
    async def verify(self, ctx):
            await ctx.message.delete()
            guild = await self.get_settings()
            try:
                if guild[str(ctx.guild.id)]["Status"] == "False":
                    return await ctx.send(f"The Captcha System is diabled!", delete_after=60)
                else: 
                    pass
            except KeyError:
                return await ctx.send(f"They are currently no settings set!")    
            try:
                Channel = guild[str(ctx.guild.id)]["VERIFYCHANNEL"]
                if not ctx.channel.id == Channel:
                    await ctx.message.delete()
                    return await ctx.send("This is not Verifychannel!", delete_after=10)
            except Exception:
                pass      
            try:
                roleID = guild[str(ctx.guild.id)]["CAPTCHAROLE"]
                pass
            except KeyError:
                return await ctx.send(f"Please setup the verifyrole first")
            role = ctx.guild.get_role(roleID)
            if role in ctx.author.roles:
                pass
            else:
                return await ctx.send("You are already verified!", delete_after=10)

            image = np.zeros(shape=(100, 350, 3), dtype=np.uint8)
            image = Image.fromarray(image + 255)  
  
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font="Tools/arial.ttf", size=60)

            text = ' '.join(
                random.choice(string.ascii_uppercase) for _ in range(6))  
            W, H = (350, 100)
            w, h = draw.textsize(text, font=font)
            draw.text(((W - w) / 2, (H - h) / 2), text, font=font, fill=(90, 90, 90))

            ID = ctx.author.id
            folderPath = f"captchaFolder/{ctx.guild.id}/captcha_{ID}"
            try:
                os.mkdir(folderPath)
            except:
                if os.path.isdir(f"captchaFolder/{ctx.guild.id}") is False:
                    os.mkdir(f"captchaFolder/{ctx.guild.id}")
                if os.path.isdir(folderPath) is True:
                    shutil.rmtree(folderPath)
                os.mkdir(folderPath)
            image.save(f"{folderPath}/captcha{ID}.png")

            p = Augmentor.Pipeline(folderPath)
            p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=14)
            p.process()

            path = f"{folderPath}/output"
            files = os.listdir(path)
            captchaName = [i for i in files if i.endswith('.png')]
            captchaName = captchaName[0]

            image = Image.open(f"{folderPath}/output/{captchaName}")
            width = random.randrange(6, 8)
            co1 = random.randrange(0, 75)
            co3 = random.randrange(275, 350)
            co2 = random.randrange(40, 65)
            co4 = random.randrange(40, 65)
            draw = ImageDraw.Draw(image)
            draw.line([(co1, co2), (co3, co4)], width=width, fill=(90, 90, 90))

            noisePercentage = 0.25  

            pixels = image.load() 
            for i in range(image.size[0]):  
                for j in range(image.size[1]):
                    rdn = random.random() 
                    if rdn < noisePercentage:
                        pixels[i, j] = (90, 90, 90)

            image.save(f"{folderPath}/output/{captchaName}_2.png")
            
            
            captchaFile = discord.File(f"{folderPath}/output/{captchaName}_2.png", filename="captcha.png")
            captcha_embed = discord.Embed(title=f"{ctx.guild.name} Captcha Verification",
                                          description=f"{ctx.author.mention} Please return me the code written on the Captcha.",
                                          colour=discord.Colour.blue())
            captcha_embed.set_image(url="attachment://captcha.png")
            try:
                await ctx.author.send(f"{ctx.author.mention}", delete_after=0.01)
                await ctx.author.send(file=captchaFile, embed=captcha_embed)
                self.value = False
            except discord.HTTPException:
                name = f"{ctx.author.name}-captcha"
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                    ctx.author: discord.PermissionOverwrite(read_messages=True)}
                channel222 = await ctx.guild.create_text_channel(name, overwrites=overwrites)
                await channel222.send(ctx.author.mention, embed=captcha_embed, file=captchaFile)
                self.value = True
            except:
                pass
            try:
                shutil.rmtree(folderPath)
            except Exception as error:
                print(f"Delete captcha file failed {error}")


            def check(message):
                if message.author == ctx.author and message.content != "":
                    return message.content

            try:
                msg = await self.bot.wait_for('message', timeout=120.0, check=check)
                password = text.split(" ")
                password = "".join(password)
                if msg.content == password:
                    if self.value == True:
                        name = f"{ctx.author.name}-captcha".lower()
                        vchannel = discord.utils.get(ctx.guild.text_channels, name=name)
                        await vchannel.send(f"{ctx.author.mention} You has been verified, You survived the captcha!")
                        await ctx.author.remove_roles(role)
                        await asyncio.sleep(10)
                        await vchannel.delete()
                    else:
                        await ctx.author.send(f"{ctx.author.mention} You has been verified, You survived the captcha!")
                        await ctx.author.remove_roles(role)
                        
                else:
                    if self.value == True:
                        name = f"{ctx.author.name}-captcha".lower()
                        vchannel = discord.utils.get(ctx.guild.text_channels, name=name)
                        await vchannel.send(f"{ctx.author.mention} you failed the captcha!, you can try again by typing the verified command again!")
                        await asyncio.sleep(5)
                        await vchannel.delete()
                    else:
                        await ctx.author.send(
                            f"{ctx.author.mention} you failed the captcha!, you can try again by typing the verified command again!")
       
            except TimeoutError:
                if self.value == True:
                        name = f"{ctx.author.name}-captcha".lower()
                        vchannel = discord.utils.get(ctx.guild.text_channels, name=name)
                        await vchannel.send(f"{ctx.author.mention} you failed the captcha!, you can try again by typing the verified command again!")
                        await asyncio.sleep(5)
                        await vchannel.delete()
                else:
                        await ctx.author.send(
                            f"{ctx.author.mention} you failed the captcha!, you can try again by typing the verified command again!")
                return    
def setup(bot):
    bot.add_cog(Verify(bot))
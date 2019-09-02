import aiohttp
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import discord
import datetime
from redbot.core.data_manager import bundled_data_path


class Stats:
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://api2.r6stats.com/public-api/"
        self.rank = {
            "Unranked": "https://i.imgur.com/jNJ1BBl.png",
            "Copper IV": "https://i.imgur.com/deTjm7V.png",
            "Copper III": "https://i.imgur.com/zx5KbBO.png",
            "Copper II": "https://i.imgur.com/RTCvQDV.png",
            "Copper I": "https://i.imgur.com/SN55IoP.png",
            "Bronve IV": "https://i.imgur.com/DmfZeRP.png",
            "Bronze III": "https://i.imgur.com/QOuIDW4.png",
            "Bronze II": "ttps://i.imgur.com/ry1KwLe.png",
            "Bronze I": "https://i.imgur.com/64eQSbG.png",
            "Silver IV": "https://i.imgur.com/fOmokW9.png",
            "Silver III": "https://i.imgur.com/e84XmHl.png",
            "Silver II": "https://i.imgur.com/f68iB99.png",
            "Silver I": "https://i.imgur.com/iQGr0yz.png",
            "Gold IV": "https://i.imgur.com/DelhMBP.png",
            "Gold III": "https://i.imgur.com/5fYa6cM.png",
            "Gold II": "https://i.imgur.com/7c4dBTz.png",
            "Gold I": "https://i.imgur.com/cOFgDW5.png",
            "Platinum III": "https://i.imgur.com/27k46er.png",
            "Platinum II": "https://i.imgur.com/0nSeDwK.png",
            "Platinum I": "https://i.imgur.com/p8J2gyx.png",
            "Diamond": "https://i.imgur.com/h02BrKN.png",
            "Diamond I": "https://i.imgur.com/h02BrKN.png",
        }
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def profile(self, profile, platform, api):
        async with self.session.get(
            self.url + f"stats/{profile}/{platform}/generic",
            headers={"Authorization": "Bearer {}".format(api)},
        ) as response:
            resp = await response.json()
            if response.status == 200:
                return resp
            else:
                return None

    async def weapontypes(self, profile, platform, api):
        async with self.session.get(
            self.url + f"stats/{profile}/{platform}/weapon-categories",
            headers={"Authorization": "Bearer {}".format(api)},
        ) as response:
            resp = await response.json()
            if response.status == 200:
                return resp
            else:
                return None

    async def weapons(self, profile, platform, api):
        async with self.session.get(
            self.url + f"stats/{profile}/{platform}/weapons",
            headers={"Authorization": "Bearer {}".format(api)},
        ) as response:
            resp = await response.json()
            if response.status == 200:
                return resp
            else:
                return None

    async def operators(self, profile, platform, api):
        async with self.session.get(
            self.url + f"stats/{profile}/{platform}/operators",
            headers={"Authorization": "Bearer {}".format(api)},
        ) as response:
            resp = await response.json()
            if response.status == 200:
                resp = resp["operators"]
                return sorted(resp, key=lambda x: x["name"])
            else:
                return None

    async def ranked(self, profile, platform, region, season, api):
        async with self.session.get(
            self.url + f"stats/{profile}/{platform}/seasonal",
            headers={"Authorization": "Bearer {}".format(api)},
        ) as response:
            resp = await response.json()
            if response.status == 200:
                try:
                    seasonss = resp["seasons"]
                    seasons = list(seasonss.keys())
                    seasons = seasons + ["None"] * 6
                    seasons.reverse()
                    return [seasons, resp["seasons"][seasons[season]]["regions"][region][0]]
                except IndexError:
                    return "Season not found"
                except TypeError:
                    return None
            else:
                return None

    async def leaderboard(self, platform, region, page, api):
        async with self.session.get(
            self.url + f"leaderboard/{platform}/{region}?page={page}",
            headers={"Authorization": "Bearer {}".format(api)},
        ) as response:
            resp = await response.json()
            if response.status == 200:
                return resp
            else:
                return None

    async def getimg(self, url):
        async with self.session.get(url) as response:
            rank = await response.read()
            return rank

    async def profilecreate(self, data):
        img = Image.new("RGBA", (400, 540), (17, 17, 17, 0))
        aviholder = self.add_corners(Image.new("RGBA", (140, 140), (255, 255, 255, 255)), 10)
        nameplate = self.add_corners(Image.new("RGBA", (200, 90), (0, 0, 0, 255)), 10)
        img.paste(nameplate, (155, 10), nameplate)
        img.paste(aviholder, (10, 10), aviholder)
        url = data["avatar_url_256"]
        im = Image.open(BytesIO(await self.getimg(url)))
        im_size = 130, 130
        im.thumbnail(im_size)
        img.paste(im, (14, 15))
        draw = ImageDraw.Draw(img)
        font2 = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 22)
        font = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 24)
        draw.text((162, 14), data["username"], fill=(255, 255, 255, 255), font=font)
        draw.text(
            (10, 180),
            "Playtime: {}".format(
                str(datetime.timedelta(seconds=int(data["stats"]["general"]["playtime"])))
            ),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (162, 40),
            "Level: {}".format(data["progression"]["level"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text((162, 70), "General Statistics", fill=(255, 255, 255, 255), font=font2)
        draw.text(
            (10, 220),
            "Total Wins: {}".format(data["stats"]["general"]["wins"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 260),
            "Total Losses: {}".format(data["stats"]["general"]["losses"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 300),
            "Draws: {}".format(data["stats"]["general"]["draws"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 340),
            "Lootbox %: {}%".format(data["progression"]["lootbox_probability"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 380),
            "Kills: {}".format(data["stats"]["general"]["kills"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 420),
            "Deaths: {}".format(data["stats"]["general"]["deaths"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 460),
            "KDR: {}".format(data["stats"]["general"]["kd"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 500),
            "Total W/LR: {}%".format(
                round(
                    data["stats"]["general"]["wins"] / data["stats"]["general"]["games_played"], 2
                )
                * 100
            ),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 540),
            "Total Ranked W/LR: {}%".format(
                round(
                    data["stats"]["queue"]["ranked"]["wins"]
                    / data["stats"]["queue"]["ranked"]["games_played"],
                    2,
                )
                * 100
            ),
            fill=(255, 255, 255, 255),
            font=font,
        )
        file = BytesIO()
        img.save(file, "png")
        file.name = "profile.png"
        file.seek(0)
        image = discord.File(file)
        return image

    async def rankedstatscreate(self, data):
        img = Image.new("RGBA", (400, 580), (17, 17, 17, 0))
        aviholder = self.add_corners(Image.new("RGBA", (140, 140), (255, 255, 255, 255)), 10)
        nameplate = self.add_corners(Image.new("RGBA", (180, 90), (0, 0, 0, 255)), 10)
        img.paste(nameplate, (155, 10), nameplate)
        img.paste(aviholder, (10, 10), aviholder)
        url = data["avatar_url_256"]
        im = Image.open(BytesIO(await self.getimg(url)))
        im_size = 130, 130
        im.thumbnail(im_size)
        img.paste(im, (14, 15))
        draw = ImageDraw.Draw(img)
        font2 = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 22)
        font = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 24)
        draw.text((162, 14), data["username"], fill=(255, 255, 255, 255), font=font)
        draw.text(
            (10, 180),
            "Playtime: {}".format(
                str(datetime.timedelta(seconds=int(data["stats"]["queue"]["ranked"]["playtime"])))
            ),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (162, 40),
            "Level: {}".format(data["progression"]["level"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text((162, 70), "Ranked Statistics", fill=(255, 255, 255, 255), font=font2)
        draw.text(
            (10, 220),
            "Total Wins: {}".format(data["stats"]["queue"]["ranked"]["wins"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 260),
            "Total Losses: {}".format(data["stats"]["queue"]["ranked"]["losses"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 300),
            "Draws: {}".format(data["stats"]["queue"]["ranked"]["draws"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 340),
            "Total Games Played: {}".format(data["stats"]["queue"]["ranked"]["games_played"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 380),
            "Kills: {}".format(data["stats"]["queue"]["ranked"]["kills"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 420),
            "Deaths: {}".format(data["stats"]["queue"]["ranked"]["deaths"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 460),
            "KDR: {}".format(data["stats"]["queue"]["ranked"]["kd"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 500),
            "Total W/LR: {}%".format(
                round(
                    data["stats"]["queue"]["ranked"]["wins"]
                    / data["stats"]["queue"]["ranked"]["games_played"],
                    2,
                )
                * 100
            ),
            fill=(255, 255, 255, 255),
            font=font,
        )
        file = BytesIO()
        img.save(file, "png")
        file.name = "ranked.png"
        file.seek(0)
        image = discord.File(file)
        return image

    async def casualstatscreate(self, data):
        img = Image.new("RGBA", (400, 580), (17, 17, 17, 0))
        aviholder = self.add_corners(Image.new("RGBA", (140, 140), (255, 255, 255, 255)), 10)
        nameplate = self.add_corners(Image.new("RGBA", (180, 90), (0, 0, 0, 255)), 10)
        img.paste(nameplate, (155, 10), nameplate)
        img.paste(aviholder, (10, 10), aviholder)
        url = data["avatar_url_256"]
        im = Image.open(BytesIO(await self.getimg(url)))
        im_size = 130, 130
        im.thumbnail(im_size)
        img.paste(im, (14, 15))
        draw = ImageDraw.Draw(img)
        font2 = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 22)
        font = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 24)
        draw.text((162, 14), data["username"], fill=(255, 255, 255, 255), font=font)
        draw.text(
            (10, 180),
            "Playtime: {}".format(
                str(datetime.timedelta(seconds=int(data["stats"]["queue"]["casual"]["playtime"])))
            ),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (162, 40),
            "Level: {}".format(data["progression"]["level"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text((162, 70), "Casual Statistics", fill=(255, 255, 255, 255), font=font2)
        draw.text(
            (10, 220),
            "Total Wins: {}".format(data["stats"]["queue"]["casual"]["wins"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 260),
            "Total Losses: {}".format(data["stats"]["queue"]["casual"]["losses"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 300),
            "Draws: {}".format(data["stats"]["queue"]["casual"]["draws"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 340),
            "Total Games Played: {}".format(data["stats"]["queue"]["casual"]["games_played"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 380),
            "Kills: {}".format(data["stats"]["queue"]["casual"]["kills"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 420),
            "Deaths: {}".format(data["stats"]["queue"]["casual"]["deaths"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 460),
            "KDR: {}".format(data["stats"]["queue"]["casual"]["kd"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 500),
            "Total W/LR: {}%".format(
                round(
                    data["stats"]["queue"]["casual"]["wins"]
                    / data["stats"]["queue"]["casual"]["games_played"],
                    2,
                )
                * 100
            ),
            fill=(255, 255, 255, 255),
            font=font,
        )
        file = BytesIO()
        img.save(file, "png")
        file.name = "casual.png"
        file.seek(0)
        image = discord.File(file)
        return image

    async def seasoncreate(self, data, season, profile):
        img = Image.new("RGBA", (400, 380), (17, 17, 17, 0))
        aviholder = self.add_corners(Image.new("RGBA", (140, 140), (255, 255, 255, 255)), 10)
        nameplate = self.add_corners(Image.new("RGBA", (240, 90), (0, 0, 0, 255)), 10)
        img.paste(nameplate, (155, 10), nameplate)
        img.paste(aviholder, (10, 10), aviholder)
        url = self.rank[list(self.rank)[data[1]["max_rank"]]]
        im = Image.open(BytesIO(await self.getimg(url)))
        im_size = 130, 130
        im.thumbnail(im_size)
        img.paste(im, (14, 15))
        draw = ImageDraw.Draw(img)
        font2 = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 22)
        font = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 24)
        draw.text((162, 14), profile, fill=(255, 255, 255, 255), font=font)
        draw.text(
            (162, 40),
            "Rank: {}".format(list(self.rank)[data[1]["max_rank"]]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (162, 70),
            f"{data[0][season].title().replace('_', ' ')} Statistics",
            fill=(255, 255, 255, 255),
            font=font2,
        )
        draw.text(
            (10, 180), "Wins: {}".format(data[1]["wins"]), fill=(255, 255, 255, 255), font=font
        )
        draw.text(
            (200, 180),
            "Losses: {}".format(data[1]["losses"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 220),
            "Abandons: {}".format(data[1]["abandons"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 260),
            "Max MMR: {}".format(data[1]["max_mmr"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 300), "End MMR: {}".format(data[1]["mmr"]), fill=(255, 255, 255, 255), font=font
        )
        draw.text(
            (10, 340),
            "End Rank: {}".format(data[1]["rank_text"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        file = BytesIO()
        img.save(file, "png")
        file.name = "season.png"
        file.seek(0)
        image = discord.File(file)
        return image

    async def operatorstatscreate(self, data, profile):
        img = Image.new("RGBA", (500, 540), (17, 17, 17, 0))
        aviholder = self.add_corners(Image.new("RGBA", (140, 140), (255, 255, 255, 255)), 10)
        nameplate = self.add_corners(Image.new("RGBA", (240, 90), (0, 0, 0, 255)), 10)
        img.paste(nameplate, (155, 10), nameplate)
        img.paste(aviholder, (10, 10), aviholder)
        url = data["badge_image"]
        im = Image.open(BytesIO(await self.getimg(url)))
        im_size = 130, 130
        im.thumbnail(im_size)
        img.paste(im, (14, 15))
        draw = ImageDraw.Draw(img)
        font2 = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 22)
        font = ImageFont.truetype(str(bundled_data_path(self) / "ARIALUNI.ttf"), 24)
        draw.text((162, 14), profile, fill=(255, 255, 255, 255), font=font)
        draw.text(
            (10, 180),
            "Playtime: {}".format(str(datetime.timedelta(seconds=int(data["playtime"])))),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (162, 40), "Operator: {}".format(data["name"]), fill=(255, 255, 255, 255), font=font
        )
        draw.text((162, 70), "Operator Statistics", fill=(255, 255, 255, 255), font=font2)
        draw.text((10, 220), "Wins: {}".format(data["wins"]), fill=(255, 255, 255, 255), font=font)
        draw.text(
            (200, 220), "Losses: {}".format(data["losses"]), fill=(255, 255, 255, 255), font=font
        )
        draw.text(
            (10, 260), "Kills: {}".format(data["kills"]), fill=(255, 255, 255, 255), font=font
        )
        draw.text(
            (200, 260), "Deaths: {}".format(data["deaths"]), fill=(255, 255, 255, 255), font=font
        )
        draw.text((10, 300), "KDR: {}".format(data["kd"]), fill=(255, 255, 255, 255), font=font)
        draw.text(
            (200, 300),
            "Headshots: {}".format(data["headshots"]),
            fill=(255, 255, 255, 255),
            font=font,
        )
        draw.text(
            (10, 360),
            "Total W/LR: {}%".format(round(data["wins"] / (data["wins"] + data["losses"]), 2)),
            fill=(255, 255, 255, 255),
            font=font,
        )
        y = 400
        try:
            for ability in data["abilities"]:

                draw.text(
                    (10, y),
                    "{}: {}".format(ability["ability"], ability["value"]),
                    fill=(255, 255, 255, 255),
                    font=font,
                )
                y += 40
        except KeyError:
            pass
        file = BytesIO()
        img.save(file, "png")
        file.name = "operator.png"
        file.seek(0)
        image = discord.File(file)
        return image

    def cog_unload(self):
        self.bot.loop.create_task(self.session.detach())

    def round_corner(self, radius):
        """Draw a round corner"""
        corner = Image.new("L", (radius, radius), 0)
        draw = ImageDraw.Draw(corner)
        draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=255)
        return corner

    def add_corners(self, im, rad):
        # https://stackoverflow.com/questions/7787375/python-imaging-library-pil-drawing-rounded-rectangle-with-gradient
        width, height = im.size
        alpha = Image.new("L", im.size, 255)
        origCorner = self.round_corner(rad)
        corner = origCorner
        alpha.paste(corner, (0, 0))
        corner = origCorner.rotate(90)
        alpha.paste(corner, (0, height - rad))
        corner = origCorner.rotate(180)
        alpha.paste(corner, (width - rad, height - rad))
        corner = origCorner.rotate(270)
        alpha.paste(corner, (width - rad, 0))
        im.putalpha(alpha)
        return im

import aiohttp
import asyncio
from selenium import webdriver

heroes = {
    "defense": [
        "Torbjörn",
        "Hanzo",
        "Widowmaker",
        "Bastion",
        "Mei"
    ],
    "dps": [
        "Soldier: 76",
        "Tracer",
        "Pharah",
        "Genji",
        "Sombra",
        "McCree",
        "Reaper",
        "Junkrat",
        "Doomfist"
    ],
    "tank": [
        "Zarya",
        "D.Va",
        "Winston",
        "Reinhardt",
        "Roadhog",
        "Orisa"
    ],
    "support": [
        "Lúcio",
        "Zenyatta",
        "Symmetra",
        "Ana"
    ]
}


class Region:
    def __init__(self):
        self.name = None
        self.tier = None
        self.winrate = None
        self.rank = None
        self.most_played = None
        self.most_played_img = None


class OWstats:
    def __init__(self):
        self.tag = None
        self.regions = []
        self.role = None
        self.avatar = None

    @classmethod
    async def get_player_stats(cls, battletag):
        self = OWstats()
        self.tag = battletag
        try:
            name = self.tag.split("#")
            owapi_session = aiohttp.ClientSession(headers={'User-Agent': 'aiohttp client 0.17'})
            async with owapi_session.get("http://owapi.net/api/v3/u/{}-{}/stats".format(name[0], name[1])) as request:
                stats = await request.json()
                for region in stats.items():
                    if region[0] == "_request":
                        continue
                    elif not region[1]:
                        continue
                    else:
                        player_region = Region()
                        player_region.name = region[0].upper()
                        player_stats = region[1]["stats"]["competitive"]
                        game_stats = player_stats["game_stats"]
                        overall_stats = player_stats["overall_stats"]
                        player_region.rank = overall_stats["comprank"]
                        player_region.tier = overall_stats["tier"].title()
                        player_region.winrate = overall_stats["win_rate"]
                        self.avatar = overall_stats["avatar"]
                        self.regions.append(player_region)
                        _get_role(battletag, player_region)

            owapi_session.close()
            return self
        except (KeyError, IndexError):
            try:
                owapi_session.close()
            except NameError:
                pass
            return "not found... Is that a real battle tag?"


def _get_role(battletag, region):
    name = battletag.split("#")
    site = "https://playoverwatch.com/en-us/career/pc/{}/{}-{}".format(region.name.lower(), name[0], name[1])
    playow_session = webdriver.PhantomJS()
    playow_session.get(site)
    competitive = playow_session.find_element_by_css_selector("a[data-mode='competitive']")
    competitive.click()
    more_heroes = playow_session.find_element_by_css_selector("#competitive button.show-more-heroes")
    more_heroes.click()
    raw_played_heroes = playow_session.find_element_by_css_selector("#competitive div[class*='progress-category'][class*='is-active']")
    played_heroes = raw_played_heroes.text.split("\n")
    raw_played_heroes_img = raw_played_heroes.find_elements_by_css_selector("img")
    played_heroes_img = [img.get_attribute("src") for img in raw_played_heroes_img]
    top_heroes = []
    top_heroes_img = []
    for hero in range(3):
        raw_name = played_heroes[hero]
        if not raw_name.startswith("Soldier: 76"):
            delimiter = raw_name.split(" ")
            delimiter.insert(1, " | ")
            delimiter.insert(3, " ")
            new_name = "".join(delimiter)
        else:
            delimiter = raw_name.split(" ")
            delimiter.insert(1, " ")
            delimiter.insert(3, " | ")
            delimiter.insert(5, " ")
            new_name = "".join(delimiter)
        top_heroes.append(new_name)
        top_heroes_img.append(played_heroes_img[hero])
    region.most_played = top_heroes
    region.most_played_img = top_heroes_img
    playow_session.close()

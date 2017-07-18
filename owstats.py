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
                        #await _get_role(battletag, player_region)

            owapi_session.close()
            return self
        except (KeyError, IndexError):
            try:
                owapi_session.close()
            except NameError:
                pass
            return "not found... Is that a real battle tag?"


def _get_role(battletag, region):
    print(region)
    name = battletag.split("#")
    site = "https://playoverwatch.com/en-us/career/pc/{}/{}-{}".format(region, name[0], name[1])
    playow_session = webdriver.PhantomJS()
    playow_session.get(site)
    competitive = playow_session.find_element_by_css_selector("a[data-mode='competitive']")
    competitive.click()
    more_heroes = playow_session.find_element_by_css_selector("#competitive button.show-more-heroes")
    more_heroes.click()
    most_played_heroes = playow_session.find_element_by_css_selector("#competitive div[class*='progress-category'][class*='is-active']")
    played_heroes = most_played_heroes.text.split("\n")
    roles = most_played_heroes.find_element_by_class_name("title")
    main = []
    for role in heroes.items():
        for hero in role[1]:
            if hero in played_heroes:
                print(hero)

    playow_session.close()

from selenium import webdriver


class Region:
    def __init__(self):
        self.name = None
        self.tier = None
        self.winrate = None
        self.rank = None
        self.most_played = None
        self.most_played_img = None


class OWstats:
    def __init__(self, battletag):
        self.tag = battletag
        self.regions = []
        self.avatar = None
        self.name = battletag.split("#")
        self.site = "https://playoverwatch.com"
        self.alt = None

        self.get_player_stats()

    def _start_playow_session(self, region):
        if self.alt is None:
            site = self.site + "/en-us/career/pc/{}/{}-{}".format(region, self.name[0], self.name[1])
        else:
            site = self.site + self.alt
        session = webdriver.PhantomJS()
        session.get(site)
        not_found = session.find_element_by_css_selector(".u-align-center").get_attribute("innerHTML")
        if not_found == "Page Not Found":
            return False
        competitive = session.find_element_by_css_selector("a[data-mode='competitive']")
        competitive.click()
        more_heroes = session.find_element_by_css_selector("#competitive button.show-more-heroes")
        more_heroes.click()

        return session

    def get_player_stats(self):
        regions = ["us", "eu", "kr"]
        for region in regions:
            player_region = Region()
            player_region.name = region.upper()
            session = self._start_playow_session(region)
            if session:
                self.set_rank(session, player_region)
                self.set_tier(session, player_region)
                self.set_most_played(session, player_region)
                self.set_avatar(session)
                self.regions.append(player_region)
                session.close()

    @staticmethod
    def set_most_played(session, region):
        raw_played_heroes = session.find_element_by_css_selector(
            "#competitive div[class*='progress-category'][class*='is-active']")
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

    @staticmethod
    def set_rank(session, region):
        player_rank = session.find_element_by_css_selector(".competitive-rank div").get_attribute("innerHTML")
        region.rank = player_rank

    @staticmethod
    def set_tier(session, region):
        player_tier = session.find_element_by_css_selector(".competitive-rank img")
        tiers = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"]
        i = 1
        for tier in tiers:
            if str(i) in player_tier.get_attribute("src").split("/")[-1]:
                region.tier = tier
                break
            i += 1

    def set_avatar(self, session):
        player_avatar = session.find_element_by_css_selector(".player-portrait")
        self.avatar = player_avatar.get_attribute("src")

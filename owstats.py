import aiohttp


async def get_player_stats(battletag):
    try:
        name = battletag.split("#")
        session = aiohttp.ClientSession(headers={'User-Agent': 'aiohttp client 0.17'})
        async with session.get("http://owapi.net/api/v3/u/{}-{}/stats".format(name[0], name[1])) as request:
            stats = await request.json()
            rank = stats["us"]["stats"]["competitive"]["overall_stats"]["comprank"]
        session.close()
        return rank
    except (KeyError, IndexError):
        try:
            session.close()
        except NameError:
            pass
        return "not found... Is that a real battle tag?"

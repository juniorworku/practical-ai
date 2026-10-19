BANK={}
def add(key,cards,scenario,reflection):
    assert len(cards)==3 and len(scenario)==5
    BANK[key]={'cards':cards,'scenario':scenario,'reflection':reflection}

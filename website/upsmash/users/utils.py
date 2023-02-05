
def get_rank(rating):
    rank = ''
    if rating > 2350:
        rank = 'Master_III'
    elif rating > 2275:
        rank = 'Master_II'
    elif rating > 2192:
        rank = 'Master_I'
    elif rating > 2137:
        rank = 'Diamond_III'
    elif rating > 2074:
        rank = 'Diamond_II'
    elif rating > 2004:
        rank = 'Diamond_I'
    elif rating > 1928:
        rank = 'Platinum_III'
    elif rating > 1843:
        rank = 'Platinum_II'
    elif rating > 1752:
        rank = 'Platinum_I'
    elif rating > 1654:
        rank = 'Gold_III'
    elif rating > 1549:
        rank = 'Gold_II'
    elif rating > 1436:
        rank = 'Gold_I'
    elif rating > 1316:
        rank = 'Silver_III'
    elif rating > 1189:
        rank = 'Silver_II'
    elif rating > 1055:
        rank = 'Silver_I'
    elif rating > 914:
        rank = 'Bronze_III'
    elif rating > 766:
        rank = 'Bronze_II'
    else:
        rank = 'Bronze_I'
    return rank

def get_rank_icon(rating):
    base_location = 'images/ranks/'
    file = 'rank_' + get_rank(rating) + '.svg'
    return base_location + file



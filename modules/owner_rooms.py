def main(bot, args):
    """rooms (only for owner)\nList rooms.\nSee also: join, leave"""

    if args: return

    if not bot.rooms:
        return 'None'
    else:
        rooms_list = u''
        for room in bot.rooms:
            rooms_list += u'%s %s\n' %(room[0], room[1])
        return rooms_list[:-1]

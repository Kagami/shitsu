def main(bot, args):
    """join <room> [pass]\nJoin a room.\nSee also: leave, rooms"""

    if len(args) == 1: room = (args[0], '')
    elif len(args) == 2: room = (args[0], args[1])
    else: return

    if bot.join(room):
        return 'done'
    else:
        return 'I\'m already in this room'

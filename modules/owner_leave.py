def main(bot, args):
    "leave <room> [pass]\nLeave a room.\nSee also: join, rooms"""

    if len(args) == 1: room = (args[0], '')
    elif len(args) == 2: room = (args[0], args[1])
    else: return

    if bot.leave(room):
        return 'done'
    else:
        return 'I\'m not in this room'

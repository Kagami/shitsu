import utils


def main(bot, args):
    """man [page]
    Show manual page.
    See also: help
    """
    if not args:
        return 'What manual page do you want?'

    if len(args) == 1:
        if bot.userCommands.has_key(args[0]):
            doc = bot.userCommands[args[0]].__doc__
        elif bot.ownerCommands.has_key(args[0]):
            doc = bot.ownerCommands[args[0]].__doc__
        else:
            doc = None
        if doc:
            return utils.trim(doc)
        else:
            return 'No manual entry for %s' % (args[0])

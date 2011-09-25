import radio

def main(bot, args):
    if args: return

    info, list = radio.getRadioState()
    return u'%s %s' %(info, list)

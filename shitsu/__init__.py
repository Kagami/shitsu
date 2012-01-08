def run(config_path=None):
    import os.path
    import optparse
    import tempfile
    from pkg_resources import resource_string
    from shitsu.main import ShiTsu

    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      help="print additional debug info")
    parser.add_option("-r", "--reload", action="store_true",
                      help="reload shitsu's config and modules on the fly")
    (options, out_args) = parser.parse_args()
    if out_args:
        parser.error("uknown options")

    dirname = os.path.dirname(__file__)
    options.modules_dirs = [os.path.join(dirname, "modules")]
    options.reload_path = os.path.join(
        tempfile.gettempdir(), "__reload_shitsu__")

    if options.reload:
        open(options.reload_path, "w").close()
        return

    if not config_path:
        config_dir = os.path.expanduser("~/.shitsu")
        config_path = os.path.join(config_dir, "shitsu.cfg")
        home_modules = os.path.join(config_dir, "modules")
        if not os.path.isfile(config_path):
            print ("Config file was not found. "
                   "Create stub in %s ?" % config_path)
            if raw_input("(y/N)") == "y":
                if not os.path.isdir(config_dir):
                    os.mkdir(config_dir)
                if not os.path.isdir(home_modules):
                    os.mkdir(home_modules)
                stub = resource_string(__name__, "shitsu.example.cfg")
                with open(config_path, "wb") as f:
                    f.write(stub)
                print "Done. Set options and run me again."
            return
        options.modules_dirs.append(home_modules)

    options.config_path = config_path
    ShiTsu(options).run()

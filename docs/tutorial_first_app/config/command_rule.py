import logging
logger = logging.getLogger(__name__ + ":expression")

def expression(intern, cmd):
    # triggers at startup
    if intern.new:

        if "hello" in cmd.key:
            arg = "world"
        elif "Don\\'t break the" in cmd.key:
            arg = "circle"
        else:
            arg = ""

        logger.info("{}: Send command arg: {}".format(cmd.key, arg))
        cmd.set = arg
    
    if cmd.new or cmd.update:
        logger.info("{}: Result: {}".format(cmd.key, cmd.value))

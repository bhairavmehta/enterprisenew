import os
import sys
import getopt
from typing import Dict

import thebox.inference.inferenceservice as svc 
from thebox.common.config import Config
from thebox.common_svc.logging import setup_service_logger

def parse_arguments(args) -> Dict:
    """Parse commandline arguments and return a dictionary of arguments
    
    Arguments:
        args {[type]} -- Arguments passed from CLI
    
    Returns:
        Dict -- dictionary of supported config values; None if invalid commands

    """

    try:
        opts, args = getopt.getopt(args, "hc:", ["config="])
    except getopt.GetoptError:
        return None

    parsed_args = {}

    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit()
        elif opt in ("-c", "--config"):
            parsed_args['config'] = arg

    return parsed_args

def print_help():
    print("""
Usage:
    python3 -m thebox_inference [-c|--config <path_to_config.yml>]
    """)

def main(args=None):

    parsed_args = parse_arguments(args)
    if parsed_args is None:
        print_help()

    default_cfg_path = os.path.join(os.path.dirname(__file__), "config.yml")
    cfg_path = parsed_args.get('config', default_cfg_path)
    cfg = Config(cfg_path)

    log = setup_service_logger(verbose=True)
    log.debug(f"Starting up using config '{cfg_path}' ...")

    svc_inst = svc.InferenceService(cfg)
    svc_inst.start(wait=True)


# start an instance of this service
if __name__ == '__main__':
    main(sys.argv[1:])

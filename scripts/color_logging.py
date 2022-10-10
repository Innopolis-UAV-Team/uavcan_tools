#!/usr/bin/env python3
import sys
import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log_info(log_str):
    print("[{}] UDP.INFO: {}".format(\
          datetime.datetime.now().strftime("%H:%M:%S"),
          log_str))
    sys.stdout.flush()

def log_warn(log_str):
    print("[{}] {}UDP.WARN: {}{}".format(\
          datetime.datetime.now().strftime("%H:%M:%S"),
          Colors.WARNING,
          log_str,
          Colors.ENDC))
    sys.stdout.flush()

def log_err(log_str):
    print("[{}] {}UDP.ERR: {}{}".format(\
          datetime.datetime.now().strftime("%H:%M:%S"),
          Colors.FAIL,
          log_str,
          Colors.ENDC))
    sys.stdout.flush()

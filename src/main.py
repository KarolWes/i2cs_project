#!/usr/bin/env python3
import logging
from garbler import LocalTest
from alice import Alice
from bob import Bob

# File is kept as received, only cleaned up for convenience
# Class YaoGarbler and LocalTest moved to file garbler.py (with no changes applied)
# Classes Alice and Bob moved to their respective files.

logging.basicConfig(format="[%(levelname)s] %(message)s",
                    level=logging.WARNING)
PRINTOUT = "none"

def main(
        party,
        circuit_path="circuits/default.json",
        oblivious_transfer=True,
        print_mode=PRINTOUT,
        loglevel=logging.DEBUG,
        filename=""
):
    logging.getLogger().setLevel(loglevel)

    if party == "alice":
        alice = Alice(circuit_path, oblivious_transfer=oblivious_transfer, print_mode=print_mode, filename=filename)
        alice.start()
    elif party == "bob":
        bob = Bob(oblivious_transfer=oblivious_transfer, print_mode=print_mode, filename=filename)
        bob.listen()
    elif party == "local":
        local = LocalTest(circuit_path, print_mode=print_mode)
        local.start()
    else:
        logging.error(f"Unknown party '{party}'")


if __name__ == '__main__':
    import argparse


    def init():
        loglevels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }

        parser = argparse.ArgumentParser(description="Run Yao protocol.")
        parser.add_argument("party",
                            choices=["alice", "bob", "local"],
                            help="the yao party to run")
        parser.add_argument(
            "-c",
            "--circuit",
            metavar="circuit.json",
            default="circuits/default.json",
            help=("the JSON circuit file for alice and local tests"),
        )
        parser.add_argument("--no-oblivious-transfer",
                            action="store_true",
                            help="disable oblivious transfer")
        parser.add_argument(
            "-m",
            metavar="mode",
            choices=["circuit", "table", "none"],
            default=PRINTOUT,
            help=f"the print mode for local tests (default '{PRINTOUT}')")
        parser.add_argument("-l",
                            "--loglevel",
                            metavar="level",
                            choices=loglevels.keys(),
                            default="warning",
                            help="the log level (default 'warning')")
        parser.add_argument("-f",
                            "--filename",
                            metavar="filename",
                            default="",
                            help="relative path to file, from which to read data (default is empty)")

        main(party=parser.parse_args().party, circuit_path=parser.parse_args().circuit,
             oblivious_transfer=not parser.parse_args().no_oblivious_transfer, print_mode=parser.parse_args().m,
             loglevel=loglevels[parser.parse_args().loglevel], filename=parser.parse_args().filename)


    init()

#!/usr/bin/python3

import sys
from delegatorbot.delegatorbot import DelegatorBot


# First we capture the command line arguments
if len(sys.argv) < 1:
    print("Please enter the command to run. Enter 'help' for a list of commands.")
else:
    command = str(sys.argv[1])
    selectedbot = str(sys.argv[2])
    if selectedbot is None:
        selectedbot = "settings"
    # import the settings based on which bot we're using
    bot = __import__(selectedbot)
    cfg = bot.Config()
    b = DelegatorBot(botname=selectedbot)

    # The various commands
    if command == "run":
        b.run_bot()

    elif command == "report":
        b.daily_report()

    elif command == "steemboost":
        b.boost_post(cfg.steem_days_old, cfg.steem_bidbot, cfg.steem_amt_to_bid)

    elif command == "sbdboost":

        b.boost_post(cfg.sbd_days_old, cfg.sbd_bidbot, cfg.sbd_amt_to_bid)

    elif command == "claim":
        b.claim()

    elif command == "balance":
        b.balance()

    elif command == "delegators":
        b.process_delegators()

    elif command == "stoppers":
        b.get_replies_to_stop()
    else:
        print ("Invalid command.")


# EOF

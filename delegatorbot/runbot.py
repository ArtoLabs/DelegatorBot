#!/usr/bin/python3

'''

        This is the entry point script for running the delegator bot.

        TODO: refactor to full blown class ;)


        ArtoLabs
        https://github.com/ArtoLabs/DelegatorBot
        https://steemit.com/@learnelectronics
        https://mike.artopium.com
        Michael Betthauser (a.k.a. Mike-A)

'''

import sys
from delegatorbot.delegatorbot import DelegatorBot 

# Entry point
def run(args=None):
    # First we capture the command line arguments
    if len(sys.argv) < 2:
        print('''
DelegatorBot Help

Command syntax: runbot [command] [botname]

The botname is optional. It should be the name of a python module copied from settings.py. Example: mybot.py

List of commands

run                 Instructs the bot to traverse the list of followers and disperse
                    upvotes, resteems and replies.

report              Creates a report containing a list of all the delegators and how much 
                    they've delegated, a list of all the posts that got upvotes in the 
                    last 24 hours, and is made using pot_template.txt as the footer. This report
                    is then posted to the Bot's Steemit account.

steemboost          Uses the STEEM bid bot set in the settings file [botname] to 
                    "boost" the most recent report.

sbdboost            Uses the SBD bid bot set in the settings file [botname] to 
                    "boost" the most recent report.

claim               Claims all rewards for the bot.

balance             prints a statement to the commandline displaying the STEEM, SBD and
                    STEEM POWER of the bot.

delegators          Searches the bot's history to see if anyone has delegated above
                    the minimum amount and follows them. The bot will unfollow a 
                    new delegation below the minimum amount.

stoppers            Searches the bot's history for relpies to posts that contain the single
                    word "STOP" in all capital letters. If so, the bot unfollows.
''')
    else:
        command = str(sys.argv[1])
        if len(sys.argv) == 3:
            selectedbot = str(sys.argv[2])
        else:
            selectedbot = "settings"
        # import the settings based on which bot we're using
        b = DelegatorBot(botname=selectedbot)

        # The various commands
        if command == "run":
            b.run_bot()

        elif command == "report":
            b.daily_report()

        elif command == "steemboost":
            b.boost_post(b.cfg.steem_days_old, "STEEM", b.cfg.steem_amt_to_bid)

        elif command == "sbdboost":
            b.boost_post(b.cfg.sbd_days_old, "SBD", b.cfg.sbd_amt_to_bid)

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

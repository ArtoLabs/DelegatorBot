#!/usr/bin/python3

'''

        The settings file for the bot.

        BE SURE TO ADJUST THE VALUES OF THIS FILE AFTER INSTALLATION 
        OR YOU WILL RECIEVE ERRORS.

        To run more than one bot, simply copy this file and rename it
        with the name of the bot e.g. mybotname.py. Adjust all the values
        for the new bot and make sure that the name of the bot, the delegation
        link, database table names, and steemit posting and active keys
        are unique to each bot. To run the bot simply type "runbot", plus
        the command, plus the name of the bot e.g. 

        runbot steemboost mybotname

        Please see the github account for full instructions.
        https://github.com/ArtoLabs/DelegatorBot

        ArtoLabs
        https://github.com/ArtoLabs/DelegatorBot
        https://steemit.com/@learnelectronics
        https://mike.artopium.com
        Michael Betthauser (a.k.a. Mike-A)

'''

class Config:

    def __init__(self):
        # The minimum balance in either STEEM or SBD that is 
        # needed for the bot to run the 'boost' feature
        self.minimum_balance = 1

        # Maximum number of times to use the 'boost' feature
        self.max_boost_count = 5

        # Messaging mode: "verbose" sends output to screen and log
        # "quiet" sends output only to log
        self.msgmode = "verbose"

        # The direct path to the log file
        self.logpath = "/home"

        # The log file name
        self.logfilename = "delegatorbot.log"

        # The Steem account used for the bot (no @ sign)
        self.mainaccount = "your-bot-name-here"

        # The steem account representing the owner of the bot (no @ sign)
        self.owner = "your-steemit-name-here"

        # The link to where people can delegate to the bot
        self.delegationlink = "https://steemconnect.com/"

        # Maximum number of days before a post is too old to get an upvote
        self.post_max_days_old = 1

        # The MySQL database user name (If not root should be granted all normal privileges)
        self.dbusername = "database-user-name"

        # The name of the MySQL database
        self.dbname = "database-name"

        # The password for the database user
        self.dbpass = "database-password"

        # The name of the table used to keep track of upvotes
        self.dbtable = "upvote-log"

        # The name of the table used to keep track of the daily report
        self.dbposttable = "daily-report"

        # The name of the table used to keep track of delegators
        self.delegatortable = "delegators"

        # The bid bot to use for 'boosting' the daily report when using STEEM
        self.steem_bidbot = "smartmarket"

        # The age of the post to be boosted when sending STEEM
        self.steem_days_old = 2

        # The amount to send to the bid bot when boosting with STEEM
        self.steem_amt_to_bid = 0.75

        # The bid bot to use for 'boosting' the daily report when using SBD
        self.sbd_bidbot = "minnowbooster"

        # The age of the post to be boosted when sending SBD
        self.sbd_days_old = 1

        # The amount to send to the bid bot when boosting with SBD
        self.sbd_amt_to_bid = 0.5

        # The minimum amount needed by delegators to have the bot follow and upvote
        self.minimum_delegation = 20

        # When the bot's vote power goes lower than this all upvotes are only 3%
        self.vote_power_threshold = 70

        # The vote weight percentage (1 to 100) the bot will give every post if the vote power threshold is crossed
        self.below_threshold_vote_weight = 10

        # A decimal number between 0 and 1 that scales the upvote weight
        self.algorithm_scale = 1

        # Sets the maximum vote weight allowed if not the owner or VIP. Must be a number between 1 and 100
        self.vote_weight_max = 100

        # Sets the minimum vote weight allowed if not an NVIP. Must be a number between 1 and 100
        self.vote_weight_min = 3

        # List of VIP accounts that if following always get a higher upvote
        self.vip_accounts = [None]

        # The percentage (1 to 100) to use if an account is in the VIP list
        self.vip_vote_weight = 100

        # List of NVIP accounts that if following always get a much lower upvote
        self.nvip_accounts = [None]

        # The percentage (1 to 100) to use if an account is in the NVIP list
        self.nvip_vote_weight = 3

        # The number of hours after a delegator makes a post during which they can only receive the reduced vote weight
        self.reduced_vote_wait_time = 3

        # The reduced vote weight percentage (1 to 100) as given if a post is made immediately after another post
        self.reduced_vote_weight = 3

        # A url to an image that is displayed on replies
        self.reply_image = "https://steemitimages.com/something"

        # The top image displayed on the daily report and the reply message
        self.footer_top_pic_url = "https://steemitimages.com/something"

        # A url to more information about the use of the bot. Should be a steemit post
        self.footer_info_url = "https://steemit.com/"

        # A url to a button displayed in the daily report that days "Delegate"
        self.footer_delegate_button_url = "https://steemitimages.com/something"

        # A url to a picture displayed at bottom of daily report
        self.footer_bottom_pic_url = "https://steemitimages.com/something"

        # A url to discord channel
        self.discord_invite_url = "https://discord.gg/your-discord-code"

        # A url to owners (personal) website
        self.website_url = "https://your.website.com"

        # The name of the owners (personal) website
        self.website_name = "Website.com"

        # The posting key, the active key
        self.keys = ['posting-key',
            'active-key']

        # The 5 tags used when posting the daily report
        self.post_tags = ["art","news","delegation","bot","upvote"]

        # Bot votes only if these tags are used by delegators
        self.allowed_tags = ["art", "music", "fashion"]




# EOF

#!/usr/bin/python3

'''

        Main module creates a class object that interacts with Steem 1.0.0
        and a MySQL database to operate a delegation bot. Those who delegate
        to the bot's account the minimum set in the settings file will cause
        the bot to start following their account. The bot can upvote, resteem
        and reply to all of those it follows.

        TODO: add better exception handling


        ArtoLabs
        https://github.com/ArtoLabs/DelegatorBot
        https://steemit.com/@learnelectronics
        https://mike.artopium.com
        Michael Betthauser (a.k.a. Mike-A)

'''

import json
import re
import os
import importlib
from screenlogger.screenlogger import Msg
from simplesteem.simplesteem import SimpleSteem
from datetime import datetime
from delegatorbot.botdb import BotDB


class DelegatorBot():    
    '''
    Main class holds functions for running the bot
    '''

    def __init__(self, debug=False, mode="verbose", botname="settings"):
        ''' Uses simplesteem and screenlogger from
            https://github.com/ArtoLabs/SimpleSteem
            https://github.com/ArtoLabs/ScreenLogger
        '''
        bot = importlib.import_module("."+botname, "delegatorbot")
        self.debug = debug
        self.cfg = bot.Config()
        self.msg = Msg(self.cfg.logfilename,
                        self.cfg.logpath,
                        mode)
        self.db = BotDB(self.cfg.dbusername, 
                                self.cfg.dbpass, 
                                self.cfg.dbname, 
                                self.cfg.dbtable, 
                                self.cfg.dbposttable,
                                self.cfg.delegatortable)
        self.steem = SimpleSteem(mainaccount=self.cfg.mainaccount,
                                keys=self.cfg.keys, 
                                screenmode=mode)
        self.voteweight = 0
        self.bidbot = None

    def get_replies_to_stop(self):
        ''' To have the delegation bot stop following
        someone and thus stop upvoting their posts
        they simply have to type STOP (in all caps)
        in a reply to the delegation bots own reply.
        '''
        c = 0
        # Get the bots history from the blockchain
        h = self.steem.get_my_history(limit=1000)
        if h is False or h is None:
            return False
        # iterate through the history
        for a in h:
            # Is it a comment (reply)?
            if a[1]['op'][0] == "comment":
                # Is it -not- from the bot?
                if not (a[1]['op'][1]['author'] 
                                == self.cfg.mainaccount):
                    # Does it contain the word STOP?
                    if re.match(r'STOP', 
                                a[1]['op'][1]['body']):
                        self.msg.error_message(
                                a[1]['op'][1]['author'] 
                                + " said STOP in this post: \n" 
                                + a[1]['op'][1]['permlink'])
                        # Get the reply's identifier
                        ident = self.steem.util.identifier(
                                a[1]['op'][1]['author'], 
                                a[1]['op'][1]['permlink'])
                        # Unfollow 
                        if not self.debug and self.steem.unfollow(
                                a[1]['op'][1]['author']):
                            # Reply to user with confirmation
                            self.steem.reply(ident, 
                                "@" + self.cfg.mainaccount + " has stopped "
                                + "following you.")
                            c += 1
        self.msg.message(str(c) + " stop messages received")
        return True

    def process_delegators(self):
        ''' The delegation bot will follow and upvote
        those who have delegated. Delegating less than
        the minimum amount will cause the bot to unfollow
        '''
        # Create the table if it doesn't already exist
        self.db.initialize_delegators()
        # set variables
        followed = 0
        unfollowed = 0
        delegators = {}
        # Get blockchain global variables 
        self.steem.global_props()
        # Get bot's history from the blockchain
        h = self.steem.get_my_history(limit=1000)
        if h is False or h is None:
            return False
        for i in h:
            # if the field is the delegate_vesting_shares 
            # field than get the name 
            # of the delegator and the sp delegated and
            # store it in the 'delegators' dictionary
            if i[1]['op'][0] == "delegate_vesting_shares":
                d = i[1]['op'][1]['delegator']
                vests = float(
                    i[1]['op'][1]['vesting_shares'].replace(
                    " VESTS", ""))
                if d != self.cfg.mainaccount:
                    delegators[d] = vests
        # get all known delegators from the database
        self.db.get_delegators()
        # iterate through new delegators
        for d, vests in delegators.items():
            sp = self.steem.util.vests_to_sp(vests)
            found = False
            follow = False
            unfollow = False
            # iterate through known delegators
            if self.db.dbresults is not None and self.db.dbresults is not False:
                for row in self.db.dbresults:
                    if d == row[1]:
                        # new delegator is already known indicating a possible change
                        found = True
                        # has it been changed?
                        if float(vests) != float(row[2]):
                            self.db.update_delegator(d, vests)
                            self.msg.message(d + " changed delegation to " 
                                                + str(vests) + " VESTS (" + str(sp) + " SP)")
                            # is it above or lower than minimum needed ?
                            if sp >= self.cfg.minimum_delegation:
                                follow = True
                            else:
                                unfollow = True
            # This is really a new delegator
            if found is False:
                # Add them to the database
                self.db.add_delegator(d, vests)
                self.msg.message("New delegation from " 
                                + d + " of " + str(vests) + " VESTS (" + str(sp) + " SP)")
                # Did they send more then the minimum?
                if sp >= self.cfg.minimum_delegation:
                    follow = True
            # Follow
            if follow:
                followed += 1
                if self.debug is False:
                    self.steem.follow(d)
            # Unfollow
            elif unfollow:
                unfollowed += 1
                if self.debug is False:
                    self.steem.unfollow(d)
        self.msg.message(str(followed) + " followed, " + str(unfollowed) + " unfollowed")
        return True

    def daily_report(self):
        ''' A report that is generated daily showing a list of current
        delegators, a list of the posts that were upvoted the day before,
        and instructions on how to get upvotes from the bot by delegating.
        '''
        # Create the table if it doesn't already exist
        self.db.initialize_bot_posts()
        # Get the date
        now = datetime.now()
        # Create the title for the report
        title = ("The @" + self.cfg.mainaccount + " Daily Report for " 
                + str(now.strftime("%B")) + " " 
                + str(now.day) + ", " 
                + str(now.year))
        self.msg.message("Creating " + title)
        # Start the body of the report
        body = ("# @" + self.cfg.mainaccount + " wants to upvote *YOUR* posts! \n"
                + "@" + self.cfg.mainaccount + ", is an upvote bot run by @" + self.cfg.owner + ". Read more "
                + "below about what @" + self.cfg.mainaccount + " does and how you can use it.")
        # Fetch the bot's current upvote value at 100% voting power
        my_vote_value = self.steem.current_vote_value(accountname=self.cfg.mainaccount,
                                                    voteweight=100,
                                                    votepoweroverride=100)
        # Add the vote value to the report
        body += ("\n\n___\n### My current upvote value at 100% is: $" 
                + str(my_vote_value) + "\n___\n\n")
        # Add The list of delegators
        del_list = self.daily_report_delegators()
        if del_list is not False and del_list is not None:
            body += del_list
        # The link to delegate to the bot
        body += ('[Delegate now]('
            + self.cfg.delegationlink 
            +') to get an upvote like these people.')
        body += ('\n\nBy delegating '
            + str(self.cfg.minimum_delegation) + ' SP or more @' 
            + self.cfg.mainaccount 
            + ' will start following you within 45 minutes and upvoting all of your posts too!')
        # Create the permlink from the title
        permlink = re.sub(r' ', '-', title)
        permlink = re.sub(r'[^A-Za-z0-9\-]', '', permlink)
        permlink = permlink.lower()
        # Add a list of all posts that received an upvote
        up_list = self.daily_report_upvote_list()
        if up_list is not False and up_list is not None:
            body += up_list
        # Add the template footer to the report
        footer = self.daily_report_footer()
        if footer is not False and footer is not None:
            body += footer
        # Check debug status
        if self.debug is False:
            self.msg.message("Posting, please wait... ")
            # post the daily report to the blockchain
            if self.steem.post(title, body, permlink, self.cfg.post_tags):        
                identifier = self.steem.util.identifier(
                                self.cfg.mainaccount, 
                                permlink)
                # Add it to the database
                self.db.add_bot_post(self.cfg.post_tags[0], identifier)
                self.msg.message("Created report " 
                                + identifier)
                return identifier
            else:
                return False
        else:
            # If debug is on just print it out to the screen
            print(body)
        return True

    def daily_report_upvote_list(self):
        ''' Creates a list of everyone that has received an upvote
        from the bot in the last 24 hours
        '''
        # get the number of upvotes in the last 24 hours
        numofposts = self.db.upvote_stats(1)
        if (self.db.dbresults is not None 
                and self.db.dbresults is not False 
                and numofposts > 0):
            # Create the list header
            upvote_list = ("\n### @" + self.cfg.mainaccount + " upvoted " 
                    + str(numofposts) 
                    + " posts yesterday. They were:<br>\n")
            # display each post upvoted and the percentage they got
            for post in self.db.dbresults:
                upvote_list = (upvote_list 
                    + "https://steemit.com/" 
                    + post[1] + "\nThis post was voted at " + str(post[3]) + "%\n\n")
            return str(upvote_list)
        else:
            self.msg.error_message("\nThe database of posts is empty\n")
            return False

    def daily_report_delegators(self):
        ''' Creates a list of the bot's delegators
        '''
        # Get the number of delegators from the database
        numofdelegators = self.db.get_delegators()
        # Are there delegators?
        if (self.db.dbresults is not None 
                and self.db.dbresults is not False 
                and numofdelegators > 0):
            # Add the delegator count to the report
            delegator_list = ("\n\n## @" + self.cfg.mainaccount + " has " 
                    + str(numofdelegators)
                    + " delegators. They are:\n\n")
            # Get the blockchain global variables
            self.steem.global_props()
            # Iterate through all the delegators and display how much they've delegated
            for d in self.db.dbresults:
                sp = int(self.steem.util.vests_to_sp(float(d[2])))
                # Those who delegate more will have their names made bigger
                if sp > 1000:
                    title_size = "##"
                elif sp > 500:
                    title_size = "###"
                elif sp > self.cfg.minimum_delegation + 5:
                    title_size = "####"
                else:
                    title_size = ""
                delegator_list = (delegator_list + title_size + " @" + d[1] 
                    + " has delegated " + str(sp) 
                    + " SP\n")
            # Thank you!
            delegator_list += "## Thank You Delegators! "
            return delegator_list
        else:
            self.msg.error_message("\nThe database of delegators is empty\n")
            return False

    def daily_report_footer(self):
        ''' opens the post_template.txt file and returns it populated with 
        values from settings.py
        '''
        # The directory we're in
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Does the file exist?
        if os.path.exists(dir_path + "/post_template.txt"):
            # Can we open it?
            with open(dir_path + "/post_template.txt",'rb') as f:
                try:
                    # split the file up into a list of lines (byte list)
                    footer = f.read().splitlines()
                except:
                    f.close()
                    self.msg.error_message("\nCould not open post_template.txt!\n")
                    return False
                else:
                    f.close()
                    # Convert, format and return
                    return ((self.make_newlines(footer)).format(self.cfg.footer_top_pic_url,
                                            self.cfg.mainaccount,
                                            self.cfg.footer_info_url,
                                            self.cfg.reply_image,
                                            self.cfg.footer_info_url,
                                            self.cfg.minimum_delegation,
                                            self.cfg.delegationlink,
                                            self.cfg.footer_delegate_button_url,
                                            self.cfg.allowed_tags,
                                            self.cfg.mainaccount,
                                            self.cfg.owner,
                                            self.cfg.footer_bottom_pic_url,
                                            self.cfg.discord_invite_url,
                                            self.cfg.website_url,
                                            self.cfg.website_name))
        else:
            self.msg.error_message("\nCould not find post_template.txt directory.\n")
            return False

    def make_newlines(self, byte_text_list=None):
        ''' Converts a list of bytes into
        one string and adds the newline character
        '''
        newtext = ''
        # decode the byte list into a string list
        try:
            ls = [i.decode() for i in byte_text_list]
        except Exception as e:
            self.msg.error_message("Byte list error: " + str(e))
            return ""
        # concatenate that list adding newlines
        if len(ls) > 0:
            for line in ls:
                newtext += str(line) + '\n'
        return newtext

    def run_bot(self):
        ''' Runs through the list of those it is following and upvotes
        the most recent post. Vote weight is determined by an algorithm (see below)
        Note that someone does not need to be a delegator to receive
        upvotes, they simply need to be followed by the bot. Of course
        delegating causes the bot to follow someone, but you can also have
        the bot follow someone manually, thus granting them upvotes without delegating.
        '''
        # If the table does not exist create it
        self.db.initialize_bot_mem()
        # Get all the account names of all those the bot is following
        if self.debug:
            following = ["artopium"]
        else:
            following = self.steem.following(self.cfg.mainaccount)
        # Are we following anyone?
        if (following is not None 
                and following is not False 
                and len(following) > 0):
            self.msg.message("Following: " + str(len(following)))
            # Iterate through that list
            for f in following:
                self.msg.message('\n' + f)
                # Did we successfully vote?
                if self.debug is False:
                    identifier = self.run_bot_upvote(f)
                else:
                    identifier = "debug"
                if identifier is not False:
                    # Resteem the post
                    if self.debug is False:
                        self.steem.resteem(identifier)
                        # Reply to the post
                        self.run_bot_reply(identifier, f)
                else:
                    self.msg.message("No post found for " + f)
        else:
            self.msg.message("The bot is not following anyone.")
            return False
        return True
        
    def run_bot_upvote(self, followed):
        ''' upvotes the post if it's eligible
        '''
        # If the table does not exist create it
        self.db.initialize_bot_mem()
        if followed is False or followed is None:
            return False
        identifier = self.steem.recent_post(followed, self.cfg.post_max_days_old, 1)
        # Is there a post?
        if identifier is False or identifier is None:
            self.msg.message("Identifier is None")
            return False
        # Are they already in the database?
        if self.db.find_bot_mem(identifier) is not False:
            self.msg.message("Already voted for " + identifier)
            return False
        # Do they have the right tags? blognumber is assigned
        # During call to get recent_post
        if self.verify_tags(self.steem.blognumber):
            # Use the algorithm to adjust vote weight, assign it to 
            # class variable so it can be accessed by run_bot_reply 
            self.voteweight = self.adjust_vote_weight(followed)
            if self.debug:
                print("would've voted: " + identifier)
                v = True
            else:
                # Vote
                v = self.steem.vote(identifier, self.voteweight)
            # Does the blockchain say we already voted?
            if v == "already voted":
                self.msg.message("Already voted for " + identifier)
                # Add it to the database
                self.db.add_bot_mem(identifier, self.voteweight)
                return False
            elif v:
                self.msg.message(followed + " got a vote at " 
                                + str(self.voteweight) + "%")
                # Add it to the database
                self.db.add_bot_mem(identifier, self.voteweight)
                return identifier
            else:
                return False
        else:
            self.msg.message(followed + " does not have the right tag.")
            return False

    def run_bot_reply(self, identifier, followed):
        ''' Resteems a post after the bot has voted on it
        '''
        if identifier is None or followed is None:
            return False
        # The directory we're in
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Does the file exist?
        if os.path.exists(dir_path + "/reply_template.txt"):
            # Can we open it?
            with open(dir_path + "/reply_template.txt",'rb') as bfile:
                try:
                    # split the file up into a list of lines (byte list)
                    reply = bfile.read().splitlines()
                except:
                    bfile.close()
                    self.msg.error_message("\nCould not open reply_template.txt!\n")
                    return False
                else:
                    bfile.close()
                    v = int(self.voteweight)
                    # format the tempalate
                    newtext = self.make_newlines(reply)
                    msg = newtext.format(followed, v,
                                        self.cfg.mainaccount,
                                        self.cfg.footer_info_url,
                                        self.cfg.reply_image,
                                        self.cfg.footer_info_url)
                    if self.debug:
                        print(identifier) 
                        print(msg)
                        return True
                    else:
                        self.steem.reply(identifier, msg)
                        return True
        else:
            self.msg.error_message("\nCould not find reply_template.txt directory.\n")
            return False



    def adjust_vote_weight(self, account):
        ''' This algorithm takes an average of all the votes made in
        the last 3 days, then subtracts that from 3-days-worth of voting power;
        The remaining vote power determines the vote weight.
        '''
        if account is None or account is False:
            return 0
        if account == self.cfg.owner:
            return 100
        if len(self.cfg.vip_accounts) > 0:
            for vip in self.cfg.vip_accounts:
                if account == vip:
                    return 100
        bal = self.steem.check_balances()
        votepower = round((self.steem.votepower 
                        + self.steem.util.calc_regenerated(
                        self.steem.lastvotetime)) / 100, 2)
        total_vote_weight_used = 1
        # make sure vote power isn't too low
        if votepower > self.cfg.vote_power_threshold:
            numofposts = self.db.upvote_stats(3)
            for i in range(0, numofposts-1):
                # for each post made we total the weight used, not the actual num of posts
                total_vote_weight_used += self.db.dbresults[i][3]
            # then we adjust based on the total weight used in the last 3 days
            # 800 is 80% of 1000, which is 10 votes at 100% per day (10 x 100)
            print (str(numofposts) + " previous posts in the last 3 days with " 
                + str(total_vote_weight_used) + " total vote weight.")
            # 3 days of vote power would is 3000
            # to account for new users and surges in use the 3000 is
            # is multiplied by a user defined number
            adj = ((3000 * self.cfg.algorithm_scale) / total_vote_weight_used * 100)
            sec_since_last_vote = self.db.already_voted_today(account)
            minutes_since_last_vote = sec_since_last_vote / 60
            print ("Base percentage: " + str(adj) + "%")
            # Caps the vote weight
            if adj > self.cfg.vote_weight_max:
                adj = self.cfg.vote_weight_max
                print ("Adjusted to "+str(self.cfg.vote_weight_max))
            print ("Minutes since last upvote: " + str(minutes_since_last_vote))
            if sec_since_last_vote is not False and int(sec_since_last_vote) < 86400:
                # if we voted them in the last 24 hours we scale the vote
                # based on how long ago the last vote was.
                if int(sec_since_last_vote) < 21600:
                    adj = 3
                else:
                    adj *= sec_since_last_vote / 86400
                print(account + " already got a vote in the last 24 hours. Adjusting vote further: " + str(adj) + "%")
                return adj
            else:
                if adj < 10:
                    adj = 10
                return adj
        else:
            return 10

    def verify_tags(self, blognumber):
        ''' Makes sure the post to be voted on has used the
        tags set in settings
        '''
        if blognumber is None:
            return False
        if self.steem.blog[blognumber]['comment']['json_metadata'] is not None:
            tags = json.loads(self.steem.blog[blognumber]['comment']['json_metadata'])
            if tags['tags'] is not None:
                for t in tags['tags']:
                    for a in self.cfg.allowed_tags:
                        if t == a:
                            return True
        else:
            self.msg.error_message("Blog comment was 'none'")
        return False
            
    def boost_post(self, daysback=0, 
                        denom="STEEM", 
                        amount=0.02):
        ''' boosts the payout of the daily report using bid bots
        '''
        if daysback < 0:
            self.msg.error_message("Invalid date to boost post")
            return False
        if denom != "STEEM" and denom != "SBD":
            self.msg.error_message("Invalid denomination to boost post")
            return False
        if amount < 0.01:
            self.msg.error_message("Invalid amount to boost post")
            return False 
        # If the table doesn't exist create it
        self.db.initialize_bot_posts()
        # Get a daiy report from the past
        identifier = self.db.get_recent_post(daysback)
        if identifier is None or identifier is False:
            self.msg.message("No posts found")
            return False
        idkey = self.db.id
        ftag = self.db.firsttag
        # Make the whole url
        boostlink = ("https://steemit.com/" 
                            + ftag + "/" 
                            + identifier)
        # make sure we have enough in the coffers
        if self.ensure_balance(denom) is not False:
            self.msg.message("Boosting " 
                            + boostlink)
            # boost
            if self.debug is False:
                self.steem.transfer_funds(
                                self.bidbot, 
                                amount, 
                                denom, 
                                boostlink)
            self.msg.message("Sent "+str(amount)+" "+denom+" to " 
                            + self.bidbot)
            return True
        else:
            return False

    def ensure_balance(self, denom):
        ''' Does what it says. Ensures that the steem or sbd balance
        of the bot account has not reached below the minimums set in settings.
        Used when "boosting"
        '''
        # If the table doesn't exist create it
        self.db.initialize_bot_posts()
        # Check the bot's balances
        bal = self.steem.check_balances(self.cfg.mainaccount)
        # Check the reward pool
        #self.steem.reward_pool_balances()
        if (denom == "SBD"):
            print ("Current SBD balance: " + str(bal[0]))
            self.bidbot = self.cfg.sbd_bidbot
            if float(bal[0]) > float(self.cfg.minimum_balance):
                return True
            else:
                self.msg.message(("Cannot boost posts because the current "
                                    + "SBD balance is {}. The balance must "
                                    + "be more than {} SBD").format(bal[0], 
                                    self.cfg.minimum_balance))
                return False
        elif (denom == "STEEM"):
            print ("Current STEEM balance: " + str(bal[0]))
            self.bidbot = self.cfg.steem_bidbot
            if bal[1] > self.cfg.minimum_balance:
                return True
            else:
                self.msg.message(("Cannot boost posts because the current "
                                    + "STEEM balance is {}. The balance must "
                                    + "be more than {} STEEM").format(bal[1], 
                                    self.cfg.minimum_balance))
                return False
        else:
            return False

    def claim(self):
        ''' Claims the rewards of the bot's account
        '''
        return self.steem.claim_rewards()


    def balance(self):
        ''' Prints the current balance
        '''
        bal = self.steem.check_balances(self.cfg.mainaccount)
        self.msg.message('''
    __{}__
    {} SBD
    {} STEEM
    {} STEEM POWER'''.format(self.steem.mainaccount,
                            bal[0], 
                            bal[1], 
                            bal[2]))
        return True


# EOF

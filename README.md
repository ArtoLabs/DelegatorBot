# DelegatorBot

DelegatorBot is a simple, yet powerful command line bot that uses delegations to determine who it upvotes, rather than bids. The concept is simple: those who delegate get an endless supply of upvotes (with limitations, of course) until they decide to undelegate (delegate zero). The bot can be configured to accept a certain amount of Steem Power as a delegation which will prompt it to follow that account. The bot can then be run to upvote, resteem and reply all of those it follows. DelegatorBot can also generate a daily report which details all of those who have delegated, how much they've delegated, as well as all of those it has upvoted, and the percentage of upvote they received.

### Bot Algorithm

Obviously, as more people delegate to the bot the demand on vote power will increase. To compensate for the ever increasing number of upvotes the bot must make a failry simple algorithm is used. At the time of each vote, the bot looks at it's history of voting in the last three days and adds up all of the vote weights. So, for example, If the bot made 10 votes in the last three days, each at 100%, the total vote weight would be 1000%. Since it's best not to upvote more than 10 100% upvotes per day (1000%), One could say that 3000% is the maximum vote weight for three days. Knowing this, to calculate the current vote weight One can simple divide 3000 by the total vote weight actually used. For example, if the actual amount of vote weight used in the last three is 4000%, then:

```
    (3000 / 4000) * 100 = 75%
```

The second part of the algorithm takes into account the idea that one delegator might post much more than other delegators. To make sure that nobody take too much from anyone else, Each delegator is given their first post of the day the maximum amount as determined by the equation above. Each post after that gets a drastically reduced percentage based on the amount of time that has elapsed since their last post. If the amount of time has only been 21600 seconds (6 hours) then the vote weight will only be 3%. After that, the voteweight is further calculated by dividing the amount of time since the last post made (in seconds) by 86400 (the number of seconds in 24 hours). So, for example:

```
    75 * (46700 / 86400) = 40.54%
```

Lastly, the algorithm accounts for a number of other possibilities. For instance, if the bot's vote weight goes below the vote weight threshold set in the settings file (see the installation instructions) then all votes for all delegators are 10% until the vote power raises back above the threshold. Also, the bot can be given a "cap" or maximum it upvotes. In this case, the maximum is 60%.

```
        if votepower > self.cfg.vote_power_threshold:
            numofposts = self.db.upvote_stats(3)
            for i in range(0, numofposts-1):
                # for each post we total the vote weight used, not the actual number of posts
                total_vote_weight_used += self.db.dbresults[i][3]
            # then we adjust based on the total weight used in the last 3 days
            # 800 is 80% of 1000, which is 10 votes at 100% per day (10 x 100)
            print (str(numofposts) + " previous posts in the last 3 days with " + str(total_vote_weight_used) + " total vote weight.")
            # although 3 days of vote power would be 3000, we use half that amount
            # to account for new users and surges in use. This helps to guarantee vote
            # power doesn't get drained too much
            adj = (1500 / total_vote_weight_used * 100)
            sec_since_last_vote = self.db.already_voted_today(account)
            minutes_since_last_vote = sec_since_last_vote / 60
            print ("Base percentage: " + str(adj) + "%")
            if adj > 60:
                adj = 60
                print ("Adjusted to 60.")
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
```

# Using Delegator Bot

Once DelegatorBot is installed, and your PATH is configured, you can run the bot simply by typing `runbot` at the commandline, which will bring up the menu below. To use these command options, type the command `runbot` followed by the command option. For example, to have the bot upvote and resteem all those it's following simply enter in `runbot run`. Running DelegatorBot this way will cause it to use the settings.py file by default. If you'd like to have more than one bot, you can create seperate settings.py file with new names, which can be used at the commandline. So, if you copied the settings.py file to a new file called `myfilename.py`, you can now run that particular bot with the command `runbot run myfilename`.

```
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

```

### run

This command option should be executed regularly so that the bot can find new posts created by delegators and give them an upvote and a reply as well as resstem them to the bot's page. As the bot gains more delegators this command can take some time to finish executing, so make sure to use a lockfile in cron or find a way to aviod collisions.

### report

This should be run daily.

### steemboost and sbdboost

These two commands can be used optionally to send bids to bid bots to "boost" the value of the daily report. You can set how much of either is sent, to which bid bots, as well as a maximum number of times to occur.

### claim

The bot can be put into a cycle of of powering down, boosting and claiming.

### balance

Prints a balance to screen. Nothing more.

### delegators

To have the bot upvote, resteem and reply, it must be following a steem account. This command causes it to run through it's recent history on the steem blockchain to see if there are any new delegations. If so it follows or unfollows based on the amount delegated. Essentilaly this means that any delegation below the minimum_delegation set in the settings file will cause the bot to stop following. To "undelegate" means to "delegate 0".

### stoppers

Optionally, a delegator can have the bot stop following them without undelegating by using this option. They simply need to reply to one of the bot's recent replies to their own post with the single word `STOP` in all capital lettes.

# Setting up automation

Using the direct path to the runbot entry point, a cron job can be set up that looks something like this (using a virtual environment):


```
#   Stoppers
26,55 * * * * /usr/bin/flock -w 10 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot stoppers artturtle
28,58 * * * * /usr/bin/flock -w 10 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot stoppers tommyknockers

#   Run bot
0 * * * * /usr/bin/flock -w 10 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot run artturtle
30 * * * * /usr/bin/flock -w 10 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot run tommyknockers

#   Daily report
15 7 * * * /usr/bin/flock /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot report artturtle
15 6 * * * /usr/bin/flock /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot report tommyknockers

#   Steem Boost
20 */2 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot steemboost artturtle
22 */2 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot steemboost tommyknockers

#   SBD Boost
45 */4 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot sbdboost artturtle
47 */4 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot sbdboost tommyknockers

#   Claim
15 8 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot claim artturtle
15 7 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot claim tommyknockers

#   Delegators
45 */4 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot delegators artturtle
47 */4 * * * /usr/bin/flock -w 20 /$HOME/$USER/cronlock/lockfile /$HOME/$USER/DelegatorBot/env/bin/runbot delegators tommyknockers

```




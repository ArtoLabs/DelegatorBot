#!/usr/bin/python3

'''

        Database managing module using MySQL statements. 
        Fetches user and post information and sends it back to the
        requesting program. Requires that you have the settings
        file setup according to the installation instructions.

        TODO: add better exception handling


        ArtoLabs
        https://github.com/ArtoLabs/DelegatorBot
        https://steemit.com/@learnelectronics
        https://mike.artopium.com
        Michael Betthauser (a.k.a. Mike-A)

'''

import sys
from mysimpledb.db import DB
from datetime import datetime
from delegatorbot.settings import Config

class BotDB(DB):

    def __init__(self, dbuser, 
                        dbpass, 
                        dbname, 
                        dbtable, 
                        dbposttable,
                        delegatortable):
        self.cfg = Config()
        try:
            DB.__init__(self, dbuser, 
                            dbpass, 
                            dbname,
                            self.cfg.logfilename,
                            self.cfg.logpath,
                            self.cfg.msgmode)
        except Exception as e:
            print ("There was an error opening the database. "
                    + "Please check that settings are correct: \n" + str(e)) 
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname
        self.dbtable = dbtable
        self.dbposttable = dbposttable
        self.delegatortable = delegatortable

    def initialize_bot_posts(self):
        ''' Creates a new table for storing a record of
        the daily report
        '''
        return self.commit("CREATE TABLE IF NOT EXISTS "
                        + self.dbposttable
                        + " (IDKey INT NOT NULL AUTO_INCREMENT "
                        + "PRIMARY KEY, PostID varchar(250), "
                        + "FirstTag varchar(30), "
                        + "Boost int(2) NOT NULL DEFAULT 0, "
                        + "Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")

    def initialize_bot_mem(self):
        ''' Creates a new table for keeping a record of which
        posts have gotten an upvote
        '''
        return self.commit("CREATE TABLE IF NOT EXISTS "
                        + self.dbtable
                        + " (IDKey INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                        + "PostID varchar(250), "
                        + "Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                        + "VoteWeight int(3));")

    def initialize_delegators(self):
        ''' Creates a new table that stores a record of the delegators
        '''
        return self.commit("CREATE TABLE IF NOT EXISTS "
                        + self.delegatortable
                        + " (ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                        + "Name varchar(250), "
                        + "Vests double, "
                        + "Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                        + "UNIQUE KEY (`Name`));")

    def already_voted_today(self, author):
        ''' Checks to see if a particular steemian has already
        received an upvote from the bot. If so, it returns
        the number of seconds since that last upvote, which is 
        then later used to adjust vote weight
        '''
        if self.get_results("SELECT Time FROM "
                        + self.dbtable                     
                        + " WHERE PostID LIKE "
                        + "%s ORDER BY Time DESC;", "%@"+author+"/%"):
            then = datetime.strptime(str(self.dbresults[0][0]), '%Y-%m-%d %H:%M:%S')
            elapsed = datetime.now() - then
            if elapsed.days > 0:
                return (elapsed.days * 86400) + elapsed.seconds
            else:
                return elapsed.seconds
        else:
            return False

    def upvote_stats(self, interval=3):
        ''' Returns the number of upvotes the bot has given out 
        in the last 24 hours.
        '''
        if self.get_results("SELECT IDKey, PostID, Time, VoteWeight FROM "
                        + self.dbtable
                        + " WHERE Time > NOW() - INTERVAL %s DAY;", interval):
            return len(self.dbresults)
        else:
            return False

    def find_bot_mem(self, identifier):
        ''' Returns a database entry for a post that got an upvote
        '''
        if self.get_results("SELECT IDKey, PostID, Time FROM "
                        + self.dbtable                     
                        + " WHERE PostID = %s;",
                        identifier):
            return self.dbresults
        else:
            return False

    def add_bot_mem(self, identifier, voteweight):
        ''' Adds to tht databse a record of which posts got an upvote
        '''
        return self.commit("INSERT INTO "
                        + self.dbtable
                        + " (PostID, VoteWeight) VALUES (%s, %s);",
                        identifier, voteweight)

    def update_boost(self, idkey):
        ''' Keeps track of how many times SBD has been used to boost
        '''
        return self.commit("UPDATE "
                        + self.dbposttable
                        + " SET Boost = Boost + 1 "
                        + "WHERE IDKey = %s;",
                        idkey)

    def get_recent_post(self, daysback=0):
        ''' Fetches the most recent daily report from the
        database. used for boosting
        '''
        if not self.get_results("SELECT IDKey, PostID, Time, "
                        + "FirstTag, Boost FROM "
                        + self.dbposttable
                        + " WHERE 1 ORDER BY Time DESC;"):
            return False
        else:
            for r in self.dbresults:
                if self.days_back(r[2]) == daysback:
                    self.id = r[0]
                    self.identifier = r[1]
                    self.time = r[2]
                    self.firsttag = r[3]
                    self.boostcount = r[4]
                    return r[1]

    def add_bot_post(self, firsttag, identifier):
        ''' Adds a record of the identifier and timestamp 
            of a daily report
        '''
        return self.commit("INSERT INTO "
                        + self.dbposttable
                        + " (PostID, FirstTag) "
                        + "VALUES (%s, %s);",
                        identifier, firsttag)

    def add_delegator(self, delegator, vests):
        ''' Adds a delegator to the databse along with the 
        amount they delegated
        '''
        return self.commit("INSERT INTO " + self.delegatortable
                        + " (Name, Vests) "
                        + "VALUES (%s, %s);",
                        delegator, vests)

    def update_delegator(self, delegator, vests):
        ''' Changes the amount the delegator has delegated. There
        is no way to remove a delegator, only to set the delegation
        amount to zero. 
        '''
        return self.commit("UPDATE " + self.delegatortable
                        + " SET Vests = " + str(vests)
                        + " WHERE Name = %s;",
                        delegator)

    def get_delegators(self):
        ''' Returns a list of all delegators that have
        a delegation larger than zero
        '''
        if self.get_results("SELECT ID, Name, Vests "
                        + "FROM " + self.delegatortable
                        + " WHERE Vests > 0 ORDER BY Vests DESC;"):
            return len(self.dbresults)
        else:
            return False

    def days_back(self, date):
        ''' Calculates a date x number of days in the past
        '''
        return (datetime.now() - date).days


# EOF

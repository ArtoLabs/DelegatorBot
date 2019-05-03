import unittest
from delegatorbot import delegatorbot, botdb, settings
from simplesteem.simplesteem import SimpleSteem


class TestDelegatorBot(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cfg = settings.Config()

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        self.bot = delegatorbot.DelegatorBot(debug=True, mode="verbose")
        self.assertTrue(self.bot.debug)
        self.assertIsInstance(self.bot.steem, SimpleSteem)
        self.assertIsInstance(self.bot.db, botdb.BotDB)
        self.assertIsInstance(self.bot.cfg, settings.Config)

    def tearDown(self):
        self.bot.s = None
        
    def test_get_replies_to_stop(self):
        self.assertIsInstance(self.bot.get_replies_to_stop(), bool)

    def test_process_delegators(self): 
        self.assertIsInstance(self.bot.process_delegators(), bool)

    def test_daily_report(self):
        self.assertIsInstance(self.bot.daily_report(), bool)

    def test_daily_report_upvote_list(self):
        self.assertIsNotNone(self.bot.daily_report_upvote_list())

    def test_daily_report_delegators(self):
        self.assertIsNotNone(self.bot.daily_report_delegators())

    def test_daily_report_footer(self):
        self.assertIsNotNone(self.bot.daily_report_footer())

    def test_make_newlines(self):
        byte_list = [b'This is line 1', b'Here is line 2', b'Yup, line 3 coming up', b'Duh, what do you think this is?']
        test_string ='This is line 1\nHere is line 2\nYup, line 3 coming up\nDuh, what do you think this is?\n'
        self.assertEqual(self.bot.make_newlines(), '')
        self.assertEqual(self.bot.make_newlines(byte_list), test_string)

    def test_daily_report(self):
        self.assertIsInstance(self.bot.daily_report(), bool)
        
    def test_run_bot(self):
        self.assertIsInstance(self.bot.run_bot(), bool)

    def test_run_bot_upvote(self):
        self.assertFalse(self.bot.run_bot_upvote(None))
        newidentifier = self.bot.run_bot_upvote("artopium")
        self.assertGreater(self.bot.voteweight, 0)
        self.assertIsNotNone(newidentifier)
        
        self.assertFalse(self.bot.run_bot_upvote("artopium"))
        if newidentifier is not None and newidentifier is not False:
            # Let's check the database
            db = botdb.BotDB(self.cfg.dbusername, 
                                    self.cfg.dbpass, 
                                    self.cfg.dbname, 
                                    self.cfg.dbtable, 
                                    self.cfg.dbposttable)
            db.get_results("SELECT IDKey, PostID FROM " 
                            + self.cfg.dbtable 
                            + " WHERE 1 ORDER BY Time DESC LIMIT 1;")
            self.assertEqual(newidentifier, db.dbresults[0][1])
            db.commit("DELETE FROM " + self.cfg.dbtable + " WHERE IDKey = " + str(db.dbresults[0][0]) + ";")
        else:
            print ("This post was already in the database. Testing skipped for this portion.")
        
    def test_run_bot_reply(self):
        self.bot.voteweight = 50
        self.assertFalse(self.bot.run_bot_reply(None, None))
        self.assertTrue(self.bot.run_bot_reply("Some identifer", "artopium"), bool)

    def test_adjust_vote_weight(self):
        self.assertEqual(self.bot.adjust_vote_weight(None), 0)
        self.assertEqual(self.bot.adjust_vote_weight(self.cfg.owner), 100)
        self.assertGreater(self.bot.adjust_vote_weight("davedickeyyall"), 2)

    def test_verify_tags(self):
        self.assertFalse(self.bot.verify_tags(None))
        identifier = self.bot.steem.recent_post("artopium", 0, 1)
        print ("Using: " + identifier)
        self.assertTrue(self.bot.verify_tags(self.bot.steem.blognumber))

    def test_boost_post(self):
        self.assertFalse(self.bot.boost_post(-1, "STEEM", 0.01))
        self.assertFalse(self.bot.boost_post(0, "Somethingelse", 0.01))
        self.assertFalse(self.bot.boost_post(0, "STEEM", 0.001))
        self.assertIsInstance(self.bot.boost_post(0, "STEEM", 0.01), bool)

    def test_ensure_balance(self):
        self.assertFalse(self.bot.ensure_balance(None))
        self.assertIsInstance(self.bot.ensure_balance("STEEM"), bool)
        self.assertIsInstance(self.bot.ensure_balance("SBD"), bool)

    #def test_claim(self):
    #    self.assertIsInstance(self.bot.claim(), bool)

    def test_balance(self):
        self.assertTrue(self.bot.balance())
        

if __name__ == '__main__':
    unittest.main()


# EOF

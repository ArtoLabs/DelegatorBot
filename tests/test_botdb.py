import unittest
import time
from delegatorbot import botdb, settings


class TestBotDB(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cfg = settings.Config()
        self.db = botdb.BotDB(self.cfg.dbusername,
                            self.cfg.dbpass,
                            self.cfg.dbname,
                            self.cfg.dbtable,
                            self.cfg.dbposttable,
                            self.cfg.delegatortable)
        self.result1 = self.db.add_bot_mem("@artopium/this-is-a-test-post-for-debugging", 100)
        self.result2 = self.db.add_bot_post("testing", "@artopium/this-is-a-fake-daily-report-for-testing")
        self.result3 = self.db.add_delegator("artopium-test", 10000.00)
        print("Sleeping 5 seconds...")
        time.sleep(5)

    @classmethod
    def tearDownClass(self):
        self.db.commit("DELETE FROM " + self.cfg.dbtable + " WHERE PostID = %s;", "@artopium/this-is-a-test-post-for-debugging")
        self.db.commit("DELETE FROM " + self.cfg.dbposttable + " WHERE PostID = %s;", "@artopium/this-is-a-fake-daily-report-for-testing")
        self.db.commit("DELETE FROM " + self.cfg.delegatortable + " WHERE Name = %s;", "artopium-test")

    def setUp(self):
        self.assertTrue(self.result1)
        self.assertTrue(self.result2)
        self.assertTrue(self.result3)

    def tearDown(self):
        pass

    def test_initialize_bot_posts(self):
        self.assertIsInstance(self.db.initialize_bot_posts(), bool)

    def test_initialize_bot_mem(self):
        self.assertIsInstance(self.db.initialize_bot_mem(), bool)

    def test_initialize_delegators(self):
        self.assertIsInstance(self.db.initialize_delegators(), bool)

    def test_already_voted_today(self):
        self.assertGreater(self.db.already_voted_today("artopium"), 0)
        self.assertFalse(self.db.already_voted_today("brad-test"))

    def test_upvote_stats(self):
        self.assertGreater(self.db.upvote_stats(1), 0)
        self.assertFalse(self.db.upvote_stats(0))

    def test_find_bot_mem(self):
        results = self.db.find_bot_mem("@artopium/this-is-a-test-post-for-debugging")
        self.assertGreater(results[0][0], 0)
        self.assertEqual(results[0][1], "@artopium/this-is-a-test-post-for-debugging")

    def test_update_boost(self):
        results = self.db.find_bot_mem("@artopium/this-is-a-test-post-for-debugging")
        self.assertTrue(self.db.update_boost(results[0][0]))

    def test_get_recent_post(self):
        self.assertEqual(self.db.get_recent_post(0), "@artopium/this-is-a-fake-daily-report-for-testing")
        self.assertIsInstance(self.db.id, int)

    def test_update_delegator(self):
        self.assertTrue(self.db.update_delegator("artopium-test", 5000.9999))
        
    def test_get_delegators(self):
        self.assertGreater(self.db.get_delegators(), 0)


if __name__ == '__main__':
    unittest.main()


# EOF

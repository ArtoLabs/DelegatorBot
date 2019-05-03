import unittest
import time
from delegatorbot import settings


class TestConfig(unittest.TestCase):

    def test_settings(self):
        self.cfg = settings.Config()
        self.assertGreater(self.cfg.minimum_balance, 0.01)
        self.assertGreater(self.cfg.max_boost_count,  0)
        self.assertIsInstance(self.cfg.max_boost_count, int)
        self.assertIsNotNone(self.cfg.msgmode)
        self.assertIsNotNone(self.cfg.logpath)
        self.assertIsNotNone(self.cfg.logfilename)
        self.assertIsNotNone(self.cfg.mainaccount)
        self.assertIsNotNone(self.cfg.owner)
        self.assertIsNotNone(self.cfg.delegationlink)
        self.assertGreater(self.cfg.post_max_days_old, 0)
        self.assertIsInstance(self.cfg.post_max_days_old, int)
        self.assertIsNotNone(self.cfg.dbusername)
        self.assertIsNotNone(self.cfg.dbname)
        self.assertIsNotNone(self.cfg.dbpass)
        self.assertIsNotNone(self.cfg.dbtable)
        self.assertIsNotNone(self.cfg.dbposttable)
        self.assertIsNotNone(self.cfg.delegatortable)
        self.assertIsNotNone(self.cfg.steem_bidbot)
        self.assertGreater(self.cfg.steem_days_old, 0)
        self.assertGreater(self.cfg.steem_amt_to_bid, 0)
        self.assertIsNotNone(self.cfg.sbd_bidbot)
        self.assertGreater(self.cfg.sbd_days_old, 0)
        self.assertGreater(self.cfg.sbd_amt_to_bid, 0)
        self.assertGreater(self.cfg.minimum_delegation, 0)
        self.assertGreater(self.cfg.vote_power_threshold, 0)
        self.assertIsNotNone(self.cfg.footer_top_pic_url)
        self.assertIsNotNone(self.cfg.footer_info_url)
        self.assertIsNotNone(self.cfg.footer_delegate_button_url)
        self.assertIsNotNone(self.cfg.footer_bottom_pic_url)
        self.assertIsNotNone(self.cfg.discord_invite_url)
        self.assertIsInstance(self.cfg.keys, list)
        self.assertIsNotNone(self.cfg.keys)
        self.assertIsInstance(self.cfg.allowed_tags, list)
        self.assertIsNotNone(self.cfg.allowed_tags)


if __name__ == '__main__':
    unittest.main()


# EOF

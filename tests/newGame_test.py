import setup
import unittest
import requests
import cultdb
import sqlite3


URL="http://localhost:5000/api/backronym/join"
DB = "CULT_copy.db"
WEBHOOK = "https%3A%2F%2Fhooks.slack.com%2Fservices%2F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"


class newGametest(unittest.TestCase):

    
    def setUp(self):
        setup.cleanSlate(DB)
    
    
    def test_prepGame(self):
        setup.gamePrepState(DB, "balls")
        host = cultdb.getHost(DB)
        self.assertEqual("balls", host)          
    

    #def test_playersJoin(self):
        payload = {'user_id': 'penis', 'token': 'TEST', 'response_url': WEBHOOK}
        post = requests.post(URL, data=payload) 
        print(post)
        players = cultdb.getContestents(DB)
        self.assertEqual(['penis'], players)

    
    
    def tearDown(self):
       setup.cleanSlate(DB)
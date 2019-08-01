from flask import abort
import os
import dotenv
import cultdb


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
verification_token = os.environ['VERIFICATION_TOKEN']
DB = os.environ['DB_FILE']
MIN_PLAYERS = int(os.environ['MIN_PLAYERS'])

### General Functions
def verify(token):
    """Verifies if the token provided matches the one set in .env"""
    return token == verification_token
#
def respond(text):
    """Creates a response in-channel."""
    return {
        "response_type" : "in_channel",
        "text" : text
    }
#
def whisper(text):
    """Creates a response only the sender can see."""
    return {
        "response_type" : "ephemeral",
        "text" : text
    }
#
def formatContestents(contestents):
    string = ""
    if len(contestents) == 1:
        string = contestents[0]
    else:
        for i,c in enumerate(contestents):
            if i < len(contestents)-2:
                string += " %s," % c
            elif i == len(contestents)-2:
                string += " %s"  % c
            else:
                string += " and %s" % c
    return string
###

### API Functions
def prep(token,user_id):
    """Performs the Preparation step."""
    if verify(token):
        state = cultdb.getGameState(DB)
        if state != 0:
            response = respond("There's a game already underway, or in the " +
                               "process of being set up! Garsh!")
        else:
            response = respond("Let's get it started with some BACKRONYMS!")
            cultdb.setHost(DB,user_id)
            cultdb.setGameState(DB,1)
        return response
    else:
        abort(
            401,"Unverified token."
        )
#
def start(token,user_id):
    """Begins the actual game. Must be done by the host who started the prep
    process."""
    if verify(token):
        state = cultdb.getGameState(DB)
        if state != 1:
            response = respond("There's already a game underway, or none at" +
                               " all! Garsh!")
        elif cultdb.getActivePlayerCount(DB) < MIN_PLAYERS:
            response = respond(("We don't have enough players :( We need at" +
                               " least %s to start, and we only have %s!") %
                               (MIN_PLAYERS,cultdb.getActivePlayerCount(DB)))
        elif cultdb.getHost(DB) != user_id:
            response = respond(("Only the host, %s, can officially start the" +
                               " game.") % cultdb.getHost(DB))
        else:
            response = respond(("All right, we have %s players! %s, your host" +
                               " is %s! Start us off with our word or phrase!")
                               % (cultdb.getActivePlayerCount(DB),
                                  formatContestents(cultdb.getContestents(DB)),
                                  cultdb.getHost(DB)))
            cultdb.setGameState(DB,2)
        return response # response defined in the above.
    else:
        abort(
            401,"Unverified token."
        )
#
def getPlayers(token):
    if verify(token):
        pass
    else:
        abort(
            401,"Unverified token."
        )
#
def getScore(token,user_id):
    if verify(token):
        pass
    else:
        abort(
            401,"Unverified token."
        )
#
def join(token,user_id):
    if verify(token):
        pass
    else:
        abort(
            401,"Unverified token."
        )
#
def help(token):
    if verify(token):
        pass
    else:
        abort(
            401,"Unverified token."
        )
#
def setWord(token,text,user_id):
    if verify(token):
        pass
    else:
        abort(
            401,"Unverified token."
        )
#
def setPhrase(token,text,user_id):
    if verify(token):
        pass
    else:
        abort(
            401,"Unverified token."
        )
###

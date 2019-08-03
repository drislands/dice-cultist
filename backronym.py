from flask import abort
import os
import dotenv
import cultdb


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
verification_token = os.environ['VERIFICATION_TOKEN']
DB = os.environ['DB_FILE']
MIN_PLAYERS = int(os.environ['MIN_PLAYERS'])
MAX_CHARACTERS = int(os.environ['MAX_CHARACTERS'])

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
#
def validateWord(text):
    """Determines if the word in question has been set correctly."""
    if ' ' in text:
        return False
    if len(text) > MAX_CHARACTERS:
        return False
    if text.upper() != text:
        return False
    if not text.isalpha():
        return False
    return True
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
            playerState = cultdb.getPlayerState(DB,user_id)
            if playerState == -1:
                cultdb.createPlayer(DB,user_id)
            cultdb.setPlayerState(DB,user_id,1)
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
            401, "Unverified token."
        )
#
def getScore(token,user_id):
    """Gets the score of the user in question."""
    if verify(token):
        score = cultdb.getPlayerScore(DB,user_id)
        if score == -1:
            response = respond("You haven't registered yet! Play a game!")
        else:
            response = respond("Your score is: %s" % score)
        return response
    else:
        abort(
            401, "Unverified token."
        )
#
def join(token,user_id):
    """Adds the player to the next round, or to the upcoming game."""
    if verify(token):
        gameState = cultdb.getGameState(DB)
        playerState = cultdb.getPlayerState(DB,user_id)

        new = False
        if playerState == -1:
            cultdb.createPlayer(DB,user_id)
            new = True

        if playerState == 1:
            response = whisper("Hey now, you're already in!")
        elif playerState == 2:
            response = whisper("Not to worry, you're already queued up for " +
                               "the next round!")
        else:
            if gameState == 0:
                response = whisper("There's no game going on right now" +
                                   (". " if not new else ", but I've created "
                                    + "an account for you. ") +
                                   "Try starting a game yourself with `/bk-prep`!")
            elif gameState == 1:
                response = respond("You are set for the upcoming game" +
                                   (", and any future ones should you choose" +
                                    " to join!" if new else "!"))
                cultdb.setPlayerState(DB,user_id,1)
                # TODO: Announce to the channel if the minimum # of players has
                # been met.
            else:
                response = whisper("Alright, you're on deck for the next " +
                                   "round!" +
                                   (" It looks like you haven't played " +
                                    "before, so I created an account for you" +
                                    " as well!" if new else ""))
                cultdb.setPlayerState(DB,user_id,2)
        return response
    else:
        abort(
            401, "Unverified token."
        )
#
def help(token):
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#
def setWord(token,text,user_id):
    if verify(token):
        state = cultdb.getGameState(DB)
        host  = cultdb.getHost(DB)
        if host != user_id:
            response = whisper("Sorry, you're not the host! Only the host " +
                               "can set the word for a given round.")
        elif state < 2:
            response = whisper("Hey, " +
                               ("a" if state == 0 else "the") +
                               " game hasn't started yet! " +
                               ("Hold your horses!" if state == 1 else
                                "Why not start one with `/bk-prep`?"))
        elif state > 2:
            response = whisper("It's not the time for that right now!")
        elif not validateWord(text):
            response = whisper(("Your word, `%s`, is not valid. Make sure " +
                                "you specify a single word, all caps, no " +
                                "more than %s letters long. And no " +
                                "punctuation either!") %
                               (text, MAX_CHARACTERS))
        else:
            cultdb.setWord(DB,text)
            cultdb.setGameState(DB,3)
            response = respond(("Alright! %s, your word is %s! Set your " +
                               "answers with `/bk-setAnswer`, and remember " +
                               "to match the word!") %
                               (formatContestents(cultdb.getContestents(DB)),
                                text))
        return response
    else:
        abort(
            401, "Unverified token."
        )
#
def setPhrase(token,text,user_id):
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#
def setAnswer(token, user_id):
    """ user sets answer to word chosen """
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#
def getAnswers(token):
    """to get the answers for the round """
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#
def getWord(token):
    """ gets the current word """
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#
def nudge(token, user_id):
    """ nudges the activated player that decided to take a nap  """
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#
def pickWinner (token, user_id):
    """ what do you think it does....it picks the winner """
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#
def dropOut (token, user_id):
    """ drops the activated player out of the game """
    if verify(token):
        pass
    else:
        abort(
            401, "Unverified token."
        )
#  
###

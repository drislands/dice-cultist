from flask import abort
import os
import dotenv
import cultdb
import requests
import time
from threading import Thread
import re


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
verification_token = os.environ['VERIFICATION_TOKEN']
DB = os.environ['DB_FILE']
MIN_PLAYERS = int(os.environ['MIN_PLAYERS'])
MAX_CHARACTERS = int(os.environ['MAX_CHARACTERS'])
WEBHOOK = os.environ['WEBHOOK']


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
#
def validatePhrase(text):
    """Determines if the word in the phrase has been set correctly."""
    pattern = "([A-Z]{2,})"
    matches = re.findall(pattern,text)
    if len(matches) != 1:
        return False
    if len(matches[0]) > MAX_CHARACTERS:
        return False
    return matches[0]
#
def announce(message,url=None):
    """Immediately sends a message to the default channel."""
    delayedAnnounce(message,0,url)
#
def delayedAnnounce(message,delay=1.5,url=None):
    """ Sends a message to the default channel with a delay."""
    t = Thread(target=threadAnnounce,args=(message,delay,url))
    t.start()
#
def threadAnnounce(message,delay,url):
    """Uses threading to make sure the announcement happens regardless."""
    time.sleep(delay)
    data = {
        "response_type" : "in_channel",
        "text":message
    }
    # This allows us to utilize the response_url parameter.
    if not url:
        url = WEBHOOK
    r = requests.post(url,json=data)
    status = r.status_code
    if status != 200:
        pass # TODO: Error handling
#
def verifyAnswer(answer):
    """Confirms whether or not the given answer matches the set word."""
    def isCap(w):
        """Returns true if the first letter is caps and no others are."""
        if not w[0].isupper():
            return False
        for c in w[1:]:
            if c.isupper():
                return False
        return True
    word = cultdb.getWord(DB)
    extras = cultdb.getMinorWords(DB)
    userWords = answer.split(' ')
    if not (isCap(userWords[0]) and isCap(userWords[-1])):
        return False
    for w in userWords[1:-1]:
        if not (w in extras or isCap(w)):
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
def join(token,user_id,response_url):
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
                cultdb.setPlayerState(DB,user_id,1)
                numPlayers = cultdb.getActivePlayerCount(DB)
                response = respond("You are set for the upcoming game" +
                                   (", and any future ones should you choose" +
                                    " to join!" if new else "!"))
                if numPlayers == MIN_PLAYERS:
                    delayedAnnounce("We are now at the minimum number of " +
                                    "players to start the game!",
                                    url=response_url)
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
        return setGeneric(text,user_id,False)
    else:
        abort(
            401, "Unverified token."
        )
#
def setPhrase(token,text,user_id):
    if verify(token):
        return setGeneric(text,user_id,True)
    else:
        abort(
            401, "Unverified token."
        )
#
def setGeneric(text,user_id,isPhrase):
    state = cultdb.getGameState(DB)
    host  = cultdb.getHost(DB)
    if isPhrase:
        word = validatePhrase(text)
    else:
        word = validateWord(text)
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
    elif not word:
        response = whisper(("Your " +
                            ("word" if not isPhrase else "phrase") +
                            ", `%s`, is not valid. Make sure " +
                            "you specify a single all caps word, no " +
                            "more than %s letters long, with no " +
                            "punctuation in the word like apostrophes.") %
                           (text, MAX_CHARACTERS))
    else:
        if isPhrase:
            cultdb.setPhrase(DB,text)
        else:
            cultdb.setWord(DB,text)
        cultdb.setGameState(DB,3)
        response = respond(("Alright! %s, your word is *%s*" +
                            (", from the phrase *%s*" %
                             text if isPhrase else "") + "! Set your " +
                           "answers with `/bk-setAnswer`, and remember " +
                           "to match the word!") %
                           (formatContestents(cultdb.getContestents(DB)),
                            (word if isPhrase else text)))
    return response
#
def setAnswer(token, user_id, text, response_url):
    """ user sets answer to word chosen """
    if verify(token):
        gameState = cultdb.getGameState(DB)
        answers = cultdb.getAnswers(DB)
        contestents = cultdb.getContestents(DB)
        if gameState != 3:
            response = whisper("It's not the time to send an answer in yet!")
        elif user_id not in contestents:
            # TODO: Have a more nuanced answer depending on the player's state
            # TODO: Have a case when the host does it erroneously
            response = whisper("You're not in this round! If you haven't " +
                               "signed up already, you can do so with " +
                               "`/bk-join`! If you're on deck, just wait " +
                               "for the next round!")
        elif user_id in answers:
            # TODO: Add the option at some point to reset your answer if you
            # want.
            response = whisper("You've already set your answer! Yours is " +
                               "`%s` in case you forgot!" % answers[user_id])
        elif not verifyAnswer(text):
            response = whisper(("The answer you provided, `%s`, isn't valid." +
                                " The word you need to match is `%s`. Make " +
                                "sure you match each letter with a " +
                                "Capitalized word, and that any extra words " +
                                "like `to` or `and` are lowercase.") %
                               (text,cultdb.getWord(DB))) # TODO: Define this function!
        else:
            cultdb.setAnswer(DB,user_id,text)
            response = whisper("Your answer has been received!")
            delayedAnnounce("%s has set their answer!" % user_id, delay = 1,
                            url = response_url)
            if len(cultdb.getAnswers(DB)) == len(contestents):
                host = cultdb.getHost(DB)
                delayedAnnounce(("%s, all answers have been sent in! See " +
                                "what they are with `/bk-getAnswers`!") % host,
                                delay = 2, url = response_url)
                cultdb.setGameState(DB,4)
        return response
            # TODO: Finish this!
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

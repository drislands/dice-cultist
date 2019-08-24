"""
    The functions defined in this module are for creating DB scenarios that may
    be tested. They are not intended for any kind of production use, and in
    fact should never be called in normal operation.
"""
import backronym
import cultdb
from cultdb import cn

#####
### Internal functions. These should not be called in the course of testing.
def plainGameState(DB,host,players,state,waiters=None):
    cleanSlate(DB)
    addPlayers(DB,host)
    addPlayers(DB,players)
    addPlayers(DB,waiters)
    activatePlayers(DB,host)
    activatePlayers(DB,players)
    activatePlayers(DB,waiters)
    cultdb.setGameState(DB,state)
    cultdb.setHost(DB,host)
###
#####
def cleanSlate(DB):
    """Resets the game, with the addition of removing all registered players."""
    cultdb.resetGame(DB)
    (c,conn) = cn(DB)
    c.execute('DELETE FROM Users')
    conn.commit()
    conn.close()
#
def addPlayers(DB,players):
    """Adds in the named players, inactive."""
    if players:
        if type(players) == str:
            cultdb.createPlayer(DB,players)
        else:
            for p in players:
                cultdb.createPlayer(DB,p)
#
def activatePlayers(DB,players):
    """Sets the named players to active status 1. Expects players exist."""
    if players:
        if type(players) == str:
            cultdb.setPlayerState(DB,players,"1")
        else:
            for p in players:
                cultdb.setPlayerState(DB,p,"1")
#
def queueUpPlayers(DB,players):
    """Sets the named players to active status 2. Expects players exist."""
    if players:
        if type(players) == str:
            cultdb.setPlayerState(DB,players,"2")
        else:
            for p in players:
                cultdb.setPlayerState(DB,p,"2")
#
def gamePrepState(DB,host,players=None):
    """Sets the game to state 1, sets the given player as host, and adds the
    listed players if any."""
    plainGameState(DB,host,players,"1")
#
def gameStartedWaitingForWordState(DB,host,players):
    """Sets the game to state 2, sets the given player as host, and adds the
    listed players."""
    plainGameState(DB,host,players,"2")
#
def gameStartedWaitingForAnswers(DB,host,players,word,isPhrase=False):
    """Sets the game state to 3, sets the given player as host, adds the listed
    players, sets the word, and optionally specifies if the word is a phrase.
    Note that there is no code making sure what you specify as a word or phrase
    is actually valid with this function."""
    plainGameState(DB,host,players,"3")
    cultdb.setGeneric(DB,word,isPhrase)

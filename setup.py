"""
    The functions defined in this module are for creating DB scenarios that may
    be tested. They are not intended for any kind of production use, and in
    fact should never be called in normal operation.
"""
import backronym
import cultdb
import cultdb.cn



def cleanSlate(DB):
    """Resets the game, with the addition of removing all registered players."""
    cultdb.resetGame(DB)
    (c,conn) = cn(DB)
    c.execute('DELETE FROM Users')
    conn.commit()
    conn.close()

def addPlayers(DB,players):
    """Adds in the named players, inactive."""
    if type(players) == str:
        cultdb.createPlayer(DB,players)
    else:
        for p in players:
            cultdb.createPlayer(DB,p)

def activatePlayers(DB,players):
    """Sets the named players to active status 1. Expects players exist."""
    if type(players) == str:
        cultdb.setPlayerState(DB,players,"1")
    else:
        for p in players:
            cultdb.setPlayerState(DB,p,"1")

def queueUpPlayers(DB,players):
    """Sets the named players to active status 2. Expects players exist."""
    if type(players) == str:
        cultdb.setPlayerState(DB,players,"2")
    else:
        for p in players:
            cultdb.setPlayerState(DB,p,"2")

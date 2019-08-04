import sqlite3

"""
Game State:
    0 - No game running.
    1 - Game prepping and looking for more players.
    2 - Game is on and we are waiting for the Host to pick a word/phrase.
    3 - Game is on and we are waiting for the contestent(s) to pick answers.
    4 - Game is on and we are waiting for the Host to pick the winner.
"""

def cn(DB):
    """Return the cursor and connection object."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    return (c,conn)

def getGameState(DB):
    """Get the state of the game."""
    (c,conn) = cn(DB)
    c.execute('SELECT value FROM Data WHERE item="stage"')
    results = c.fetchall()
    if len(results) != 1:
        pass #this should throw an exception.
    conn.close()
    return int(results[0][0])

def setGameState(DB,stage):
    """Set the state of the game. Should be from 0-4."""
    (c,conn) = cn(DB)
    c.execute('UPDATE Data SET value="%s" WHERE item="stage"' % stage)
    conn.commit()
    conn.close()

def createPlayer(DB,player):
    """Creates a new player with the specified ID, and a score and state of
    zero. Note that this does not check if the player already exists."""
    (c,conn) = cn(DB)
    c.execute('INSERT INTO Users VALUES("%s",0,0)' % player)
    conn.commit()
    conn.close()

def setPlayerState(DB,player,state):
    (c,conn) = cn(DB)
    c.execute('UPDATE Users SET active="%s" WHERE userID="%s"' %
              (state,player))
    conn.commit()
    conn.close()

def getPlayerState(DB,player):
    (c,conn) = cn(DB)
    c.execute('SELECT active FROM Users WHERE userID="%s"' % player)
    results = c.fetchall()
    if len(results) != 1:
        return -1  # indicates the player does not have an entry.
    conn.close()
    return int(results[0][0])

def deactivatePlayer(DB,player):
    state = getPlayerState(DB,player)
    if state == -1: # this means the player isn't entered. Handle appropriately.
        pass
    elif state == 0: # this means the player isn't active.
        pass
    elif state == 1: # this means they are.
        (c,conn) = cn(DB)
        # Indicate that the player has been deactivate, and end the game if
        # necessary.
        c.execute('UPDATE Users SET active="0" WHERE userID="%s"' % player)
        conn.commit()
        conn.close()
    elif state == 2: # this means they're on deck.
        (c,conn) = cn(DB)
        # Indicate that the player is no longer on deck. This should not end
        # the game.
        c.execute('UPDATE Users SET active="0" WHERE userID="%s"' % player)
        conn.commit()
        conn.close()
    else: # this should throw an exception.
        pass

def getActivePlayerCount(DB):
    """Gets the number of active players."""
    (c,conn) = cn(DB)
    c.execute('SELECT COUNT(*) FROM Users WHERE active="1"')
    results = c.fetchone()
    conn.close()
    return int(results[0])

def getWaitingPlayerCount(DB):
    """Gets the number of players waiting for the next round."""
    (c,conn) = cn(DB)
    c.execute('SELECT COUNT(*) FROM Users WHERE active="2"')
    results = c.fetchone()
    conn.close()
    return int(results[0])

def getHost(DB):
    (c,conn) = cn(DB)
    c.execute('SELECT value FROM Data WHERE item="host"')
    results = c.fetchall()
    conn.close()
    if len(results) != 1:
        pass # this should not happen.
    else:
        res = results[0][0]
        return res

def setHost(DB,user_id):
    """Sets the game host."""
    (c,conn) = cn(DB)
    c.execute('UPDATE Data SET value="%s" WHERE item="host"' % user_id)
    conn.commit()
    conn.close()

def getContestents(DB):
    """Returns a list of all the contestents' usernames."""
    (c,conn) = cn(DB)
    host = getHost(DB)
    if host == "unset":
        pass # This means there is no host.
    c.execute('SELECT userid FROM Users WHERE userid!="%s" AND active="1"' % host)
    results = c.fetchall()
    res = [x[0] for x in results]
    return res

def resetGame(DB):
    (c,conn) = cn(DB)
    c.execute('UPDATE Data SET value="0" WHERE item="stage" OR item="isPhrase"')
    c.execute('UPDATE Data SET value="unset" WHERE item="host" OR item="word"')
    c.execute('UPDATE Users SET active="0"')
    conn.commit()
    conn.close()

def getPlayerScore(DB,user_id):
    """Returns the score of the identified player."""
    (c,conn) = cn(DB)
    c.execute('SELECT score FROM Users WHERE userId="%s"' % user_id)
    results = c.fetchall()
    if len(results) > 1:
        pass # this means there are duplicate entries. exception!
    elif len(results) == 0:
        # this means there is no entry. whoops!
        return -1
    else:
        return results[0][0]

def setWord(DB,word):
    """Sets the word in question."""
    (c,conn) = cn(DB)
    c.execute('UPDATE Data SET value="%s" WHERE item="word"' % word)
    c.execute('UPDATE Data SET value="0" WHERE item="isPhrase"')
    conn.commit()
    conn.close()

def setPhrase(DB,word):
    """Sets the phrase in question."""
    (c,conn) = cn(DB)
    c.execute('UPDATE Data SET value="%s" WHERE item="word"' % word)
    c.execute('UPDATE Data SET value="1" WHERE item="isPhrase"')
    conn.commit()
    conn.close()

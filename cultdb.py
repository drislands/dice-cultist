import sqlite3

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

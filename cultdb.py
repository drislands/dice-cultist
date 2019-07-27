import sqlite3


def getGameState(DB):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT value FROM Data WHERE item="stage"')
    results = c.fetchall()
    if len(results) != 1:
        pass #this should throw an exception.
    conn.close()
    return int(results[0][0])

def setGameState(DB,stage):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('UPDATE Data SET value="%s" WHERE item="stage"' % stage)
    conn.commit()
    conn.close()


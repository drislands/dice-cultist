from flask import abort
import os
import dotenv
import cultdb


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
verification_token = os.environ['VERIFICATION_TOKEN']
DB = os.environ['DB_FILE']
MIN_PLAYERS = int(os.environ['MIN_PLAYERS'])


def verify(token):
    return token == verification_token


def prep(token):
    if verify(token):
        state = cultdb.getGameState(DB)
        if state != 0:
            pass # This means a game is already underway.
        else:
            # TODO: Do the code that lets everyone know a game is starting.
            cultdb.setGameState(DB,1)
            return response # response needs to be defined in the above.
    else:
        abort(
            401,"Unverified token."
        )

def start(token,user_id):
    if verify(token):
        state = cultdb.getGameState(DB)
        if state != 1:
            pass # This means the game isn't in a state to start.
        elif cultdb.getActivePlayerCount(DB) < MIN_PLAYERS:
            pass # This means we don't have enough players yet.
        else:
            # TODO: Let everyone know the game is on, and prompt the host to
            # pick a word or phrase.
            cultdb.setGameState(DB,2)
            return response # response defined in the above.
    else:
        abort(
            401,"Unverified token."
        )

from flask import abort
import os
import dotenv
import cultdb

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
verification_token = os.environ['VERIFICATION_TOKEN']
db_file = os.environ['DB_FILE']


def verify(token):
    return token == verification_token


def prep(token):
    if verify(token):
        # do the thing!
        pass
    else:
        abort(
            401,"Unverified token."
        )

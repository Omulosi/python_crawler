import os
import json

def load_chrome_sessions(session_filename):
    cookies = {}
    if os.path.exists(session_filename):
        json_data = json.loads(open(session_filename, 'r').read())
    else:
        print('Session filename does not exist:', session_filename)
    return json_data

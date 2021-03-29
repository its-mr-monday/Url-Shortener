
def create_short_url_query(url_long, url_short, username):
    return f"INSERT INTO urltable (url_shortened, url_long, url_user) VALUES (\'{url_short}\', \'{url_long}\', \'{username}\');"

def create_manage_info_query(username):
    return f"SELECT * FROM users WHERE uname = \"{username}\";"
    
def url_query(shortened_link):

    return f"SELECT * FROM urltable WHERE url_shortened = \"{shortened_link}\";"
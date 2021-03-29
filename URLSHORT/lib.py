import random
import string
import requests

def SQL_SYNTAX_CHECK(input: str) -> bool:
    bad_char = ['*',';','SELECT ',' FROM ', ' TRUE ', ' WHERE ']
    for char in bad_char:
        if char in input:
            return False
    return True


def validateRegistration(name, uname, email, password, confirm):
    if len(name) < 1 or len(name) > 45:
        return "Error invalid name"

    if len(uname) < 1 or len(uname) > 20:
        return "Error invalid username"

    if len(email) < 1 or len(email) > 100:
        return "Error invalid email"

    if len(password) < 1:
        return "Error invalid password"
    
    if password != confirm:
        return "Error passwords do not match"

    return "Success"
    
def validate_email(email: str):
    at_counter = 0
    for x in email:
        if x == "@":
            at_counter+=1
    
    if at_counter == 1:
        return True
    else:
        return False

def validate_link(link: str):
    req = requests.get('http://www.example.com')
    if req.status_code == 200:
        return True
    else:
        return False

def generate_link() -> str:
    letters = string.ascii_lowercase+string.ascii_uppercase+"0123456789"
    return (''.join(random.choice(letters) for i in range(10)))
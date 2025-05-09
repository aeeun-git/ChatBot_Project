
users = {
    1: ["hohoyeol", "1234"],
    2: ["minji", "abcd"]
}

def get_password_by_username(username):
    for _, (name, pwd) in users.items():
        if name == username:
            return pwd
    return None

def user_exists(username):
    return any(name == username for _, (name, _) in users.items())

import bcrypt, json, jwt, time

def generate_token(username):
    token = jwt.encode({'username': username, 'exp': time.time() + 3600}, 'secret', algorithm='HS256')
    return token

def decode_token(token, secret):
    try:
        username = jwt.decode(token, secret, algorithms=['HS256'])['username']
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return None
    return username

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(password, hashed_password):
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        return True
    else:
        return False

def check_password_against_db(username, password):
    with open('./login.json', 'r') as f:
        data = json.load(f)
        if username not in data:
            return False
        hashed_password = data[username]['password']
        if check_password(password, hashed_password):
            return True
        else:
            return False

def register(username, password):
    with open('./login.json', 'r') as f:
        data = json.load(f)
        hashed_password = hash_password(password)
        data[username] = {'password': hashed_password}
        with open('./login.json', 'w') as f:
            json.dump(data, f)
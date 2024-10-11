import bottle, json, uuid, os, time
import bottle.ext.websocket as bws # type: ignore
import serverutils as su, securelogin as sl

SERVER_SECRET = os.environ.get('SERVER_SECRET') or uuid.uuid4().hex

app = bottle.Bottle()
bottle.TEMPLATE_PATH = ['./templates']

database = json.load(open('./database.json'))

@app.route('/')
def index():
    if not bottle.request.get_cookie('token'):
        return bottle.redirect('/login')
    return bottle.template('index.stpl', data=database)

@app.route('/login')
def loginView():
    return bottle.template('login.stpl')

@app.route('/register')
def registerView():
    return bottle.template('register.stpl')

@app.route('/devpage')
def devpage():
    return bottle.static_file('devpage.html', root='./static')

@app.route('/d1362b46-48db-407d-a9bb-3a87c8634aa6')
def maincss():
    return bottle.static_file('main.min.css', root='./')

@app.route('/static/<filename>')
def static(filename):
    return bottle.static_file(filename, root='./static')

@app.route('/uuid/<uuid>')
def serve_by_uuid(uuid):
    item = su.find_item_by_uuid(database, uuid)
    if item is None:
        return bottle.abort(404, "Item not found")
    return bottle.template("itemCardView.stpl",name=item, data=database[item])

@app.route('/tpl/itemview/<item>', method='GET')
def itemview(item):    
    if item not in database:
        return bottle.abort(404, "Item not found")
    return bottle.template("itemCardView.stpl",name=item, data=database[item])

@app.route('/tpl/itemviewuuid/<uuid>', method='GET')
def itemviewuuid(uuid):
    item = su.find_item_by_uuid(database, uuid)
    if item is None:
        return bottle.abort(404, "Item not found")
    return bottle.template("itemCardView.stpl",name=item, data=database[item])

@app.route('/tpl/itemUpdate/<uuid>', method='GET')
def itemUpdate(uuid):
    item = su.find_item_by_uuid(database, uuid)
    if item is None:
        return bottle.abort(404, "Item not found")
    return bottle.template("itemUpdate.stpl",name=item)

@app.route('/tpl/imageUpload/<uuid>', method='GET')
def imageUpload(uuid):
    item = su.find_item_by_uuid(database, uuid)
    if item is None:
        return bottle.abort(404, "Item not found")
    return bottle.template("imageUpload.stpl",name=item)

@app.route('/tpl/create')
def create():
    return bottle.template('create.stpl')

@app.route('/api/item/<item>/get', method='GET')
def item(item):
    if item not in database:
        return bottle.abort(404, "Item not found")
    return database[item]

@app.put('/api/item/<item>/create')
def create(item):
    if not sl.decode_token(bottle.request.get_cookie('token'), SERVER_SECRET):
        return bottle.abort(401, "Unauthorized")
    global database
    if item in database:
        return bottle.abort(409, "Item already exists")
    database[item] = {"name": item, "uuid": su.generate_id(), "description": None, "images": {}, "amount": 0}
    json.dump(database, open('./database.json', 'w'))
    return bottle.HTTPResponse("Item created", status=201)

@app.post('/api/item/<item>/update')
def update(item):
    if not sl.decode_token(bottle.request.get_cookie('token'), SERVER_SECRET):
        return bottle.abort(401, "Unauthorized")
    global database
    if item not in database:
        return bottle.abort(404, "Item not found")
    try:
        arc = bottle.request.json
    except ValueError:
        return bottle.HTTPResponse("Invalid JSON", status=400)
    if not arc:
        return bottle.HTTPResponse("No JSON data", status=400)
    if 'description' in arc and arc['description']:
        database[item]['description'] = arc['description']
    if 'amount' in arc and arc['amount']:
        database[item]['amount'] = arc['amount']
    if 'name' in arc and arc['name']:
        database[item]['name'] = arc['name']
    json.dump(database, open('./database.json', 'w'))
    return bottle.HTTPResponse(status=204)

@app.route('/api/item/<item>/delete', method='DELETE')
def delete(item):
    if not sl.decode_token(bottle.request.get_cookie('token'), SERVER_SECRET):
        return bottle.abort(401, "Unauthorized")
    global database
    if item in database:
        images = database[item]['images']
        for image in images:
            os.remove('./images/' + image)
        del database[item]
        json.dump(database, open('./database.json', 'w'))
        return bottle.HTTPResponse(status=204)
    else:
        return bottle.abort(404, "Item not found")

@app.route('/api/item/<item>/image', method="PUT")
def upload_image(item):
    upload = bottle.request.files.get('upload')
    if not upload:
        return bottle.abort(400, "No image to upload")
    _, ext = os.path.splitext(upload.filename)
    if ext not in ['.png', '.jpg', '.jpeg', '.webp']:
        return bottle.abort(400, "Only .png, .jpg, .jpeg, .webp images are allowed")
    id = su.generate_id()
    dest = os.path.join('./images/', id + ext)
    upload.save(dest, overwrite=True)
    database[item]['images'][id] = {"timestamp": int(time.time())}
    json.dump(database, open('./database.json', 'w'))
    return bottle.HTTPResponse(id, status=201)

@app.route('/api/images/<uuid>', method="GET")
def get_image(uuid):
    for file in os.listdir('./images/'):
        if file.startswith(uuid):
            return bottle.static_file(file, root='./images/')
    return bottle.abort(404, "Image not found")

@app.post('/api/login')
def login():
    try:
        arc = bottle.request.json
    except ValueError:
        return bottle.HTTPResponse("Invalid JSON", status=400)
    if not arc:
        return bottle.HTTPResponse("No JSON data", status=400)

    if not 'username' in arc or not 'password' in arc:
        return bottle.HTTPResponse("No username or password provided", status=400)
    
    if not arc['username'] or not arc['password']:
        return bottle.HTTPResponse("No username or password provided", status=400)
    
    if not sl.check_password_against_db(arc['username'], arc['password']):
        return bottle.HTTPResponse("Invalid username or password", status=401)
    token = sl.generate_token(arc['username'], SERVER_SECRET)

    bottle.response.set_cookie('token', token, path='/')

@app.put('/api/users/<user>')
def register(user):
    try:
        arc = bottle.request.json
    except ValueError:
        return bottle.HTTPResponse("Invalid JSON", status=400)
    if not arc:
        return bottle.HTTPResponse("No JSON data", status=400)
    
    if 'password' in arc and arc['password']:
        sl.register(user, arc['password'])
        return bottle.HTTPResponse(status=201)
    else:
        return bottle.HTTPResponse("No password provided", status=400)

@app.route('/api/item/all', method='GET')
def all():
    return json.dumps({"items": list(database.keys())})


app.run(server=bws.GeventWebSocketServer)

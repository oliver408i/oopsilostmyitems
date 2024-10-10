import bottle, json, uuid, os, time
import bottle.ext.websocket as bws # type: ignore
import serverutils as su

app = bottle.Bottle()
bottle.TEMPLATE_PATH = ['./templates']

database = json.load(open('./database.json'))

@app.route('/')
def index():
    return bottle.static_file('index.html', root='./static')

@app.route('/devpage')
def devpage():
    return bottle.static_file('devpage.html', root='./static')

@app.route('/d1362b46-48db-407d-a9bb-3a87c8634aa6')
def maincss():
    return bottle.static_file('maincss.css', root='./')

@app.route('/static/<filename>')
def static(filename):
    return bottle.static_file(filename, root='./static')

@app.route('/uuid/<uuid>')
def serve_by_uuid(uuid):
    item = su.find_item_by_uuid(database, uuid)
    if item is None:
        return bottle.abort(404, "Item not found")
    return bottle.template("itemCardView.stpl",name=item, data=database[item])

# to be removed
@app.route('/tpl/itemview/<item>/', method='GET')
def itemview(item):
    return bottle.template("itemCardView.stpl",name=item, data=database[item])

@app.route('/api/item/<item>/get', method='GET')
def item(item):
    if item not in database:
        return bottle.abort(404, "Item not found")
    return database[item]

@app.post('/api/item/<item>/update')
def update(item):
    global database
    if item not in database:
        database[item] = {"name": item, "uuid": su.generate_id(), "description": None, "images": {}, "amount": 0}
        json.dump(database, open('./database.json', 'w'))
        return bottle.HTTPResponse("Item created", status=201)
    try:
        arc = bottle.request.json
    except ValueError:
        return bottle.HTTPResponse("Invalid JSON", status=400)
    if not arc:
        return bottle.HTTPResponse("No JSON data", status=400)
    if 'description' in arc:
        database[item]['description'] = arc['description']
    if 'amount' in arc:
        database[item]['amount'] = arc['amount']
    if 'name' in arc:
        database[item]['name'] = arc['name']
    json.dump(database, open('./database.json', 'w'))
    return bottle.HTTPResponse(status=204)

@app.route('/api/item/<item>/delete', method='DELETE')
def delete(item):
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


@app.route('/api/item/all', method='GET')
def all():
    return json.dumps({"items": list(database.keys())})


app.run(server=bws.GeventWebSocketServer)
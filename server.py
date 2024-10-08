import bottle, json

app = bottle.Bottle()
bottle.TEMPLATE_PATH = ['./templates']

database = json.load(open('./database.json'))

@app.route('/')
def index():
    return bottle.static_file('index.html', root='./static')

@app.route('/d1362b46-48db-407d-a9bb-3a87c8634aa6')
def maincss():
    return bottle.static_file('maincss.css', root='./')

@app.route('/static/<filename>')
def static(filename):
    return bottle.static_file(filename, root='./static')

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
        database[item] = {}
        json.dumps(database, open('./database.json', 'w'))
        return bottle.HTTPResponse("Item created", status=201)
    try:
        arc = bottle.request.json
    except ValueError:
        return bottle.HTTPResponse("Invalid JSON", status=400)
    if not arc:
        return bottle.HTTPResponse("No JSON data", status=400)
    database[item] = arc
    json.dump(database, open('./database.json', 'w'))
    return bottle.HTTPResponse(status=204)

@app.route('/api/item/<item>/delete', method='DELETE')
def delete(item):
    global database
    if item in database:
        del database[item]
        json.dump(database, open('./database.json', 'w'))
        return bottle.HTTPResponse(status=204)
    else:
        return bottle.abort(404, "Item not found")

@app.route('/api/item/all', method='GET')
def all():
    return json.dumps({"items": list(database.keys())})
bottle.debug(True)
app.run()
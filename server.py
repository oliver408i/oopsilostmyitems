import bottle, json

app = bottle.Bottle()

database = json.load(open('./database.json'))

@app.route('/')
def index():
    return bottle.static_file('index.html', root='./static')

@app.route('/static/<filename>')
def static(filename):
    return bottle.static_file(filename, root='./static')

@app.route('/api/item/<item>/', method='GET')
def item(item):
    if item not in database:
        return bottle.abort(404, "Item not found")
    return database[item]

@app.route('/api/item/<item>/update/', method='POST')
def update(item):
    if item not in database:
        return bottle.HTTPResponse("Item created", status=201)
    try:
        arc = bottle.request.json
    except ValueError:
        return bottle.HTTPResponse("Invalid JSON", status=400)
    database[item] = arc
    json.dump(database, open('./database.json', 'w'))
    return bottle.HTTPResponse(status=204)

@app.route('/api/item/<item>/delete/', method='DELETE')
def delete(item):
    if item in database:
        del database[item]
        json.dump(database, open('./database.json', 'w'))
        return bottle.HTTPResponse(status=204)
    else:
        return bottle.abort(404, "Item not found")

@app.route('/api/item/all/', method='GET')
def all():
    return json.dumps({"items": list(database.keys())})

app.run()
from app import app

@app.route('/parking/', methods=['GET'])
def parking():
    return 'Deu certo'
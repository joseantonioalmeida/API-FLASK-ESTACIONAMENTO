from app import app

@app.route('/vehicles/', methods=['GET'])
def vehicle():
    return 'Deu certo'
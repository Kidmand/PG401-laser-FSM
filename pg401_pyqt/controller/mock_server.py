from flask import Flask, request

app = Flask(__name__)

@app.route('/REST/HTTP_CMD/', methods=['GET'])
def mock_response():
    #return "%d<br>%d<br>%d<br>%s <br>%s <br>%f" % (1, 2, 3, "hola", "chau", 3.14)
    return "1<br><code>hola</code>||;||<br>" % (1,"hola")

if __name__ == '__main__':
    app.run(host='localhost', port=8081)




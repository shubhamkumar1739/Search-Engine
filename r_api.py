import flask
import utilities
import Processing

app = flask.Flask(__name__)

@app.route('/search', methods = ["GET"])
def search(results) :
	print(request)

if __name__ == '__main__' :
	app.run(debug = True)
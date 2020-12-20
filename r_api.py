import flask
import utilities
import Processing
import request

app = flask.Flask(__name__)

@app.route('/search', methods = ["GET"])
def search() :
	print(request.form["results"])

if __name__ == '__main__' :
	app.run(debug = True)
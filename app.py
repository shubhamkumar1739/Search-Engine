import flask
from flask import request
import utilities
import Processing

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/search/', methods = ["GET"])
def search() :
	res = Processing.run(request.args.get("results"))
	return {"results" : res}

if __name__ == '__main__' :
	app.run(debug = True)	
from flask import Flask, request, jsonify

app = Flask(__name__)
# Temporary page that help me see if the server work.
@app.route('/')
def home():
    return "<h1>hello</h1>"

# API 1: Hello
@app.route('/hello', methods=['GET'])
def hello():
    return '', 200

if __name__ == "__main__":
    app.run(debug=True ,port=8080)
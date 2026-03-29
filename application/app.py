from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/get")
def get_data():
    return jsonify({"method": "GET", "status": "ok"})

@app.post("/post")
def post_data():
    return jsonify({"method": "POST", "data": request.get_json(silent=True)})

@app.put("/put")
def put_data():
    return jsonify({"method": "PUT", "data": request.get_json(silent=True)})

app.run(host="0.0.0.0", port=5000)
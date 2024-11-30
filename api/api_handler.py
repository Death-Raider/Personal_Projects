"""
This file acts as a router and coordinator, delegating tasks to other functions
(within server.py) that handle the core logic.
The list of routes this files needs to handle are as follows:
* User verification (aadhar,pan,etc) [POST,GET]
* Research papers [GET]
* Researcher verification [GET]
* Forum base chat room [POST,GET]
* Researcher-Voluenteer chat room [POST,GET]
* User profile details [POST,GET]
"""


from flask import Flask, json, request, jsonify
from server import get_user, create_post, create_user
from models import User, Post

app = Flask(__name__)

@app.route("/mail", methods=["POST"])
def mail():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    # do something with request
    request_json = request.get_json()
    return 

@app.route("/profile", methods=["GET"])
def profiles():
    # do something with request
    print("test")
    mail = request.args.get("email")
    if mail != None:
        user = get_user(mail)
        return jsonify(user)
    else:
        return jsonify({"error": "Arguments weren't provided"}), 400

@app.route("/create_user", methods=["POST"])
def create_user_endp():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user: User = User(
        name=data["name"], 
        pfp=data["pfp"], 
        description=data["description"], 
        USER_TYPE=data["USER_TYPE"], 
        verification=data["verification"], 
        gender=data["gender"], 
        age=data["age"], 
        researcher=data["researcher"]
    )
    userCreated = create_user(user, data["uid"], data["email"], data["password"])
    print(userCreated)
    return jsonify({"success": "done"}), 200

@app.route("/create_post", methods=["POST"])
def create_post():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    # do something with request
    request_json = request.get_json()



    return True

if __name__ == "__main__":
    print("running on localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)

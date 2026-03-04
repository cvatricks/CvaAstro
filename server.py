import datetime
from datetime import datetime, timedelta
from config import Config
from flask import Flask, request, jsonify, render_template
from werkzeug.security import check_password_hash

app = Flask(__name__)

# MongoDB Connection
users_collection = Config.users  # Collection where users are stored
active_sessions = Config.sessions # Collection where sessions are stored
workdbdata = Config.workdata # traceablity data
jobdb = Config.jobid # traceablity data

@app.route("/", methods=["GET"])
def indexPage():
    return render_template("/index.html", HOST=Config.HOST, PORT=Config.PORT)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login_id = data.get("loginId")
    password = data.get("password")
    # Find user in MongoDB
    user = users_collection.find_one({"login_id": login_id})

    if user and (user["password"] == password):
        login_id = login_id
        login_time = str(datetime.now() + timedelta(hours=5, minutes=30))
        session = {
            "login_id": login_id,
            "login_time": login_time
        }
        sessions = active_sessions.insert_one(session)
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    data = request.json
    login_id = data.get("loginId")
    # Find user in MongoDB
    user = users_collection.find_one({"login_id": login_id})
    if user:
        login_id = login_id
        session = {
            "login_id": login_id
        }
        sessions = active_sessions.delete_one(session)
        return jsonify({"success": True, "message": "Logout successful"})
    else:
        return jsonify({"success": False, "message": "Logout failed"}), 401

@app.route("/dashboard", methods=["GET"])
def dashboardPage():
    return render_template("/dashboard.html", HOST=Config.HOST, PORT=Config.PORT)


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    data = request.json
    user = data.get("user")
    report = "<tr style='background-color:#FBCEB1;'><td>Process</td><td>Work</td><td>DateTime</td><td>Job ID</td></tr>"
    if user == "admin":
        workdata = ""
    else:
       workdata = {
           "process_name" : "{}".format(user)
       }
    workdataupdated = workdbdata.find(workdata)
    for x in workdataupdated:
        itsdata = f'<tr><td>{x.get("process_name")}</td><td>{x.get("work")}</td><td>{x.get("datetime")}</td><td>{x.get("jobid")}</td></tr>'
        report = report + itsdata
    if report != "<tr style='background-color:#FBCEB1;'><td>Process</td><td>Work</td><td>DateTime</td><td>Job ID</td></tr>":
        return jsonify({"success": True, "message": report})
    else:
        return jsonify({"success": False, "message": "No records Found!"})

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host=Config.IP, port=Config.PORT)


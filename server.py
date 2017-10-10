from flask import Flask
from flask import render_template
from sqlalchemy import func
from gevent.wsgi import WSGIServer
from flask import send_from_directory
from flask import make_response
from flask import request
from flask import redirect
from flask import jsonify
from sqlUtil import *

app = Flask(__name__)
host = "58.196.143.65"
hostL = "0.0.0.0"
port = 8000
dbSession = initDB()
itemsPerPage = 3

@app.route("/")
@app.route("/home")
def home():
    return render_template("Home.html", pages=0, resultFlag=False)

@app.route("/login")
def login():
    return render_template("Login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        userid = request.form['userid']
        eaddress = request.form['eaddress']
        password = request.form['password']
        try:
            with app.app_context():
                dbSession.add(User(
                    id=userid, firstname=firstname, lastname=lastname,
                    eaddress=eaddress, password=password
                    ))
                dbSession.commit()
        finally:
            return jsonify(err = '', redirect = 'login')
    else:
        return render_template("Register.html")
@app.route("/loginUser", methods=["POST"])
def userLogin():
    userid = request.form['userid']
    password = request.form['password']
    result = None
    with app.app_context():
        try:
            result = dbSession.query(User).filter(User.id == userid, User.password == password).first()
        finally:
            if(result == None):
                return jsonify(err = 'invalid', redirect = '')
            else:
                response = make_response(jsonify(err = '', redirect = 'home'))
                response.set_cookie('userid', userid)
                return response
    return jsonify(err = 'invalid', redirect = '')
@app.route("/register/validation", methods=["POST"])
def registerValid():
    data = request.get_json()
    result = None
    field = data['field']
    with app.app_context():
        if(field == "email"):
            try:
                result = dbSession.query(User).filter(User.eaddress == data['data']).first()
            finally:
                if(result != None):
                     return 'EMAIL_ALREADY_EXIST'
                else:
                    return ''
        elif(field == "id"):
            try:
                result = dbSession.query(User).filter(User.id == data['data']).first()
            finally:
                if(result != None):
                    return "USERNAME_ALREADY_EXIST"
                else:
                    return ''
        else:
            return ''
@app.route("/getPic/<path:path>")
def getPic(path):
  #paths = path.split('/')
  return send_from_directory("./pics/", path)
@app.route("/searchByMechanical", methods=["POST"])
def searchByMechanical():
    metric = request.form['metric']
    value = request.form['value']
    per = request.form['per']
    if (value == None or value == "" or per == None or per == ""):
        return render_template("Home.html", pages=0, resultFlag=True)
    maxVal = float(value) * (1 + float(per) / 100)
    minVal = float(value) * (1 - float(per) / 100)
    result = dbSession.execute('select * from mechanical where {} <= {} and {} >= {}'.format(metric, maxVal, metric, minVal))
    tp = set()
    res = []
    for row in result:
        if(not row.alloyName in tp):
            res.append(row)
            tp.add(row.alloyName)
    pages = len(res) // itemsPerPage + (1 if len(res) % itemsPerPage != 0 else 0)
    data = []
    for i in range(pages):
        tpData = []
        for j in range(itemsPerPage):
            idx = i * itemsPerPage + j
            if(idx < len(res)):
                item = res[idx]
                idUrl = "http://{}:{}/searchByAlloy?alloyName={}".format(host, port, item.alloyName)
                picUrl = "http://{}:{}/getPic/{}.jpg".format(host, port, item.alloyName)
                tpData.append([item.alloyName, item.alloyType, idUrl, picUrl])
        data.append(tpData)
    return render_template("Home.html", data=data, pages=pages, resultFlag=True)
@app.route("/searchByPhysics", methods=["POST"])
def searchByPhysics():
    metric = request.form['metric']
    value = request.form['value']
    per = request.form['per']
    if(value == None or value == "" or per == None or per == ""):
        return render_template("Home.html", pages=0, resultFlag=True)
    maxVal = float(value) * (1 + float(per) / 100)
    minVal = float(value) * (1 - float(per) / 100)
    result = dbSession.execute('select * from physics where {} <= {} and {} >= {}'.format(metric, maxVal, metric, minVal))
    result = [x for x in result]
    pages = len(result) // itemsPerPage + (1 if len(result) % itemsPerPage != 0 else 0)
    data = []
    for i in range(pages):
        tpData = []
        for j in range(itemsPerPage):
            idx = i * itemsPerPage + j
            if(idx < len(result)):
                item = result[idx]
                idUrl = "http://{}:{}/searchByAlloy?alloyName={}".format(host, port, item.alloyName)
                picUrl = "http://{}:{}/getPic/{}.jpg".format(host, port, item.alloyName)
                tpData.append([item.alloyName, item.alloyType, idUrl, picUrl])
        data.append(tpData)
    return render_template("Home.html", data=data, pages=pages, resultFlag=True)
@app.route("/searchByElement", methods=["POST"])
def searchByElement():
    elements = {}
    for i in range(1, 5):
        element = request.form['element{}'.format(i)]
        per = request.form['per{}'.format(i)]
        if(element != None and per != None and per != ""):
            try:
                elements[element] = float(per)
            except Exception as e:
                return render_template("Home.html", pages=0, resultFlag=True)
    if(len(elements) == 0):
        return render_template("Home.html", pages=0, resultFlag=True)
    res = []
    for element, per in elements.items():
        records = dbSession.query(Ingredient).filter(Ingredient.elementName == element, Ingredient.maxPer >= per, Ingredient.minPer <= per).all()
        tpRes = []
        for record in records:
            tpRes.append(record.alloyName)
        res.append(tpRes)
    last = res[0]
    for i in range(1, len(res)):
        if(res[i] == None or len(res[i]) == 0):
            return render_template("Home.html", pages=0, resultFlag=True)
        last = list(set(last) & set(res[i]))
    res = []
    for id in last:
        record = dbSession.query(PhysicsPerformance).filter(PhysicsPerformance.alloyName == id).first()
        if(record != None):
            res.append(record)
    pages = len(res) // itemsPerPage + (1 if len(res) % itemsPerPage != 0 else 0)
    data = []
    for i in range(pages):
        tpData = []
        for j in range(itemsPerPage):
            idx = i * itemsPerPage + j
            if(idx < len(res)):
                item = res[idx]
                idUrl = "http://{}:{}/searchByAlloy?alloyName={}".format(host, port, item.alloyName)
                picUrl = "http://{}:{}/getPic/{}.jpg".format(host, port, item.alloyName)
                tpData.append([item.alloyName, item.alloyType, idUrl, picUrl])
        data.append(tpData)
    return render_template("Home.html", data=data, pages=pages, resultFlag=True)


@app.route("/searchByAlloy", methods=["POST", "GET"])
def searchByAlloy():
    alloyName = ""
    if request.method == "GET":
        alloyName = request.args.get("alloyName")
    else:
        alloyName = request.form['alloyname']
    if(alloyName == None or alloyName == ""):
        return render_template("Home.html", pages=0, resultFlag=True)
    else:
        alloyName = alloyName.lower()
        data = {}
        physicsResult = dbSession.query(PhysicsPerformance).filter(func.lower(PhysicsPerformance.alloyName) == alloyName).first()
        ingredientResult = [x.as_dict() for x in dbSession.query(Ingredient).filter(func.lower(Ingredient.alloyName) == alloyName).all()]
        mechanicalResult = dbSession.query(MechanicalPerformance).filter(func.lower(MechanicalPerformance.alloyName) == alloyName).first()
        if(physicsResult != None or mechanicalResult != None):
            alloyName = physicsResult.alloyName if physicsResult != None else mechanicalResult.alloyName
            picUrl = "http://{}:{}/getPic/{}.jpg".format(host, port, alloyName)
            data['alloyName'] = alloyName
            data['physicsResult'] = physicsResult.as_list() if physicsResult != None else None
            data['ingredientResult'] = ingredientResult
            alloyType = data['physicsResult'][1] if physicsResult != None else mechanicalResult.alloyType
            if(mechanicalResult != None):
                mechanicalResult = mechanicalResult.as_list()
                del mechanicalResult[2]
                if(alloyType in ["Al合金", "Mg合金", "焊料合金"]):
                    mechanicalResult = mechanicalResult[1:-6]
                elif(alloyType == "不锈钢"):
                    mechanicalResult = mechanicalResult[1:3] + mechanicalResult[4:9] + mechanicalResult[10:11] + mechanicalResult[-6:-4]
                else:
                    mechanicalResult = mechanicalResult[1:7] + mechanicalResult[-4:]
            data['mechanicalResult'] = mechanicalResult
            return render_template("Alloy.html", data=data, picUrl=picUrl, alloyType=alloyType)
        else:
            return render_template("Home.html", pages=0, resultFlag=True)
if __name__ == "__main__":
  http_server = WSGIServer((hostL, port), app)
  http_server.serve_forever()
  #app.run(host, port, True)
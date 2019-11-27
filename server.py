from passlib.hash import bcrypt
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from http import cookies
from users import usersDB
from dndSheet import dndSheetDB
from session_store import SessionStore
import sys

gSessionStore = SessionStore()
datauser = {}
datachara = {}

class MyHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.sendcookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.loadsession()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        return

    def do_GET(self):
        print("PATH:", self.path)
        self.loadsession()
        path = self.path.split("/")[-1]
        if self.path == "/Characters":
            self.handleGetAllCharacterSheets()
        elif self.path == "/Characters/" + path:
            self.handleGetCharacterSheet(path)
        elif self.path == "/sessiontest":
            if "counter" in self.session:
                self.session["counter"] += 1
            else:
                self.session["counter"] = 1
            self.send_response(200)
            self.sendcookie()
            self.end_headers()
            self.wfile.write(bytes(str(self.session["counter"]), "urf-8"))
        else:
            self.handle404(path)

    def do_POST(self):
        print("PATH:", self.path)
        self.loadsession()
        if self.path == "/Characters":
            self.handleCreateSheet()
        elif self.path == "/Users/":
            self.handleCreateUser()
        elif self.path == "/Sessions":
            self.handleUsersLogin()
        else:
            self.handle404general()

    def do_PUT(self):
        print("PATH:", self.path)
        self.loadsession()
        path = self.path.split("/")[-1]
        if self.path == "/Characters/" + path:
            self.handleUpdateSheet(path)
        elif self.path == "/Sessions":
            self.handleUsersLogin()
        else:
            self.handle404(path)

    def do_DELETE(self):
        print("PATH:", self.path)
        self.loadsession()
        path = self.path.split("/")[-1]
        if self.path == "/Characters/" + path:
            self.handleDeleteSheet(path)
        elif self.path == "/Sessions":
            self.handleUsersLogin()
        else:
            self.handle404(path)

    def handle404(self, path):
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("404 Not Found", "utf-8"))

    def handle404general(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("404 Not Found", "utf-8"))

    def loadsession(self):
        self.loadcookie()
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value
            sessionData = gSessionStore.getSession(sessionId)
            if sessionData != None:
                self.session = sessionData
            else:
                sessionId = gSessionStore.createSession()
                self.cookie["sessionId"] = sessionId
                self.session = gSessionStore.getSession(sessionId)
        else:
            sessionId = gSessionStore.createSession()
            self.cookie["sessionId"] = sessionId
            self.session = gSessionStore.getSession(sessionId)


    def loadcookie(self):
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

    def sendcookie(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())
   
    def handleUsersLogin(self):
        data01 = usersDB()
        len01 = int(self.headers["Content-length"])
        body = self.rfile.read(len01).decode("utf-8")
        parsed_body = parse_qs(body)

        email = parsed_body['email'][0]
        password = parsed_body["password"][0]
        userid = data01.exists(email)

        if userid != None:
            getpass = data01.checkPassword(userid)
            verpass = bcrypt.verify(password, getpass)
            if verpass == True:
                self.session["userId"] = userid
                userid = data01.getUserId(email)
                json_string = json.dumps(userid)
                self.send_response(201)
                self.end_headers()
                self.wfile.write(bytes(json_string, "utf-8"))
            else:
                self.send_response(401)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("401", "utf-8"))
        else:
            self.send_response(401)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("401", "utf-8"))

    def handleCreateUser(self):
        data01 = usersDB()
        len01 = int(self.headers["Content-length"])
        body = self.rfile.read(len01).decode("utf-8")
        parsed_body = parse_qs(body)

        password = parsed_body["password"][0]
        newpassword = bcrypt.encrypt(password)

        datauser = {
            "fname": parsed_body['fname'][0],
            'lname': parsed_body['lname'][0],
            'email': parsed_body['email'][0],
            'password': newpassword
        }

        email = datauser['email']
        if data01.exists(email) == None:
            data01.createUser(datauser)
            self.send_response(201)
            self.end_headers()
            self.wfile.write(bytes("POSTED", "utf-8"))
            print("user made")
        else:
            self.send_response(422)
            self.end_headers()
            self.wfile.write(bytes("422", "utf-8"))
            print("user already there")



    def handleGetAllCharacterSheets(self):
        if "userId" not in self.session:
            # 401
            self.send_response(401)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("401", "utf-8"))
            return
        db = dndSheetDB()
        rows = db.getCharacterSheets()
        json_string = json.dumps(rows)
        print(json_string)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json_string, "utf-8"))
        print(db)

    def handleGetCharacterSheet(self, path):
        if "userId" not in self.session:
            # 401
            self.send_response(401)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("401", "utf-8"))
            return

        db = dndSheetDB()
        row = db.getCharacterSheet(path)
        if db.exists(path) == False:
            self.handle404(path)
            return False
        json_string = json.dumps(row)
        print(json_string)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json_string, "utf-8"))
        print("db: ", db)

    def handleCreateSheet(self):
        if "userId" not in self.session:
            # 401
            self.send_response(401)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("401", "utf-8"))
            return
        length = int(self.headers["Content-length"])
        body = self.rfile.read(length).decode("utf-8")
        parsed_body = parse_qs(body)
        print("Request body:", parsed_body)
        self.send_response(201)
        self.end_headers()
        self.wfile.write(bytes("Post", "utf-8"))
        datachara = {
            "name": parsed_body['name'][0],
            "player": parsed_body['player'][0],
            "classs": parsed_body['classType'][0],
            "lvl": parsed_body['lvl'][0],
            "race": parsed_body['race'][0],
            "age": parsed_body['age'][0],
            "gender": parsed_body['gender'][0],
            "strength": parsed_body['str'][0],
            "dexterity": parsed_body['dex'][0],
            "constitution": parsed_body['con'][0],
            "intellect": parsed_body['int'][0],
            "wisdom": parsed_body['wis'][0],
            "charisma": parsed_body['cha'][0],
        }
        print("Name: ", datachara["name"])
        print("Player: ", datachara["player"])
        print("Class: ", datachara["classs"])
        db = dndSheetDB()
        db.createCharacterSheet(datachara)

    def handleDeleteSheet(self, path):
        if "userId" not in self.session:
            # 401
            self.send_response(401)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("401", "utf-8"))
            return
        db = dndSheetDB()
        if db.exists(path) == False:
            self.handle404(path)
            return False
        db.deleteCharacterSheet(path)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def handleUpdateSheet(self, path):
        if "userId" not in self.session:
            # 401
            self.send_response(401)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("401", "utf-8"))
            return

        db = dndSheetDB()
        if db.exists(path) == False:
            self.handle404(path)
            return False
        length = int(self.headers["Content-length"])
        body = self.rfile.read(length).decode("utf-8")
        parsed_body = parse_qs(body)
        print("Request body:", parsed_body)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("UPDATED", "utf-8"))

        data = {
            "name": parsed_body['name'][0],
            "player": parsed_body['player'][0],
            "classs": parsed_body['classType'][0],
            "lvl": parsed_body['lvl'][0],
            "race": parsed_body['race'][0],
            "age": parsed_body['age'][0],
            "gender": parsed_body['gender'][0],
            "strength": parsed_body['str'][0],
            "dexterity": parsed_body['dex'][0],
            "constitution": parsed_body['con'][0],
            "intellect": parsed_body['int'][0],
            "wisdom": parsed_body['wis'][0],
            "charisma": parsed_body['cha'][0],
        }
        db.upDateCharacterSheet(data, path)


def main():
    db1 = dndSheetDB()
    db1.createCharacterSheetTable()
    db1 = None #disconnect

    db2 = usersDB()
    db2.createUserTable()
    db2 = None #disconeect

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyHandler)

    print("Server listening on", "{}:{}".format(*listen))
    server.serve_forever()

main()

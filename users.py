import os
import psycopg2
import psycopg2.extras
import urllib.parse


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class usersDB:

    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createUserTable(self):
        sql = 'CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, fname VARCHAR(255), lname VARCHAR(255), email VARCHAR(255), password VARCHAR(255))'
        self.cursor.execute(sql)
        self.connection.commit()

    def findFirstName(self, id):
        sql = 'SELECT * FROM users where id = %s;'
        self.cursor.execute(sql, (id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row['fname']

    def findLastName(self, id):
        sql = 'SELECT * FROM users where id = %s;'
        self.cursor.execute(sql, (id,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row['lname']

    def getUserId(self, email):
        sql = 'SELECT * FROM users WHERE email = %s;'
        self.cursor.execute(sql, (email,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row['email']

    def exists(self, email):
        sql = 'SELECT * FROM users WHERE email = %s;'
        self.cursor.execute(sql, (email,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row['id']

    def checkPassword(self, id):
        sql = 'SELECT * FROM users WHERE id = %s;'
        self.cursor.execute(sql, (id,))
        row = self.cursor.fetchone()
        if row is None:
            return False
        return row['password']

    def createUser(self, data):
        sql = '''
                INSERT INTO users
                (fname, lname, email, password)
                VALUES (%s, %s, %s, %s)
              '''
        attributes = (
                data['fname'], data['lname'], data['email'], data['password']
        )
        self.cursor.execute(sql, attributes)
        self.connection.commit()

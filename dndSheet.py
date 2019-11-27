import os
import psycopg2
import psycopg2.extras
import urllib.parse

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class dndSheetDB:

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


    def createCharacterSheetTable(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS dndSheet
            (id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            player VARCHAR(255),
            classs VARCHAR(255),
            lvl INTEGER,
            race VARCHAR(255),
            age INTEGER,
            gender VARCHAR(255),
            strength INTEGER,
            dexterity INTEGER,
            constitution INTEGER,
            intellect INTEGER,
            wisdom INTEGER,
            charisma INTEGER)
        '''
        self.cursor.execute(sql)
        self.connection.commit()


    def exists(self, id):
        sql = 'SELECT * FROM dndSheet WHERE id = %s;'
        self.cursor.execute(sql, (id,))
        row = self.cursor.fetchone()
        if row is None:
            return False
        return row

    def createCharacterSheet(self, data):
        sql = '''
                INSERT INTO dndSheet
                (name, player, classs, lvl, race, age, gender,
                strength, dexterity, constitution, intellect, wisdom, charisma)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              '''
        attributes = (
                data['name'], data['player'], data['classs'], data['lvl'], data['race'], data['age'],
                data['gender'], data['strength'], data['dexterity'], data['constitution'], data['intellect'],
                data['wisdom'], data['charisma']
        )
        self.cursor.execute(sql, attributes)
        # self.cursor.execute("INSERT INTO dndSheet (name, player, classs, lvl, race, age, gender, strength, dexterity, constitution, intellect, wisdom, charisma) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, player, classs, lvl, race, age, gender, strength, dexterity, constitution, intellect, wisdom, charisma))
        self.connection.commit()

    def deleteCharacterSheet(self, path):
        if not self.exists(path):
            return False
        sql = 'DELETE FROM dndSheet WHERE id=%s'
        self.cursor.execute(sql, (path,))
        self.connection.commit()

    def getCharacterSheets(self):
        sql = 'SELECT * FROM dndSheet'
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows

    def getCharacterSheet(self, path):
        if not self.exists(path):
            return False
        sql = 'SELECT * FROM dndSheet WHERE id=%s'
        self.cursor.execute(sql, (path,))
        row = self.cursor.fetchone()
        self.connection.commit()
        return row

    def upDateCharacterSheet(self, data, id):
        if not self.exists(id):
            return False
        self.cursor.execute("UPDATE dndSheet \
            SET \
            name = %s, player = %s, classs = %s, lvl = %s, race = %s, age = %s, gender = %s, \
            strength = %s, dexterity = %s, constitution = %s, intellect = %s, wisdom = %s, charisma = %s \
            WHERE id = %s",
            (
            data['name'],
            data['player'],
            data['classs'],
            data['lvl'],
            data['race'],
            data['age'],
            data['gender'],
            data['strength'],
            data['dexterity'],
            data['constitution'],
            data['intellect'],
            data['wisdom'],
            data['charisma'],
            id
            )
        )
        # self.cursor.execute(sql)
        self.connection.commit()
        return True

    # SELECT * FROM dndSheet WHERE id = 1;

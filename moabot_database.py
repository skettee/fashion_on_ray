import sqlite3 
from datetime import datetime

# Dbase class for sqlite
class Dbase():
    def __init__(self, db_name, bot_id):
        # Certificate and initialize app
        # Create database and save cursor or reference
        self.db_name = db_name + '.db'
        self.table_name = bot_id
        self.data = {
            'title': '',
            'desc': '',
            'url': '',
            'image': '',
            'siteName': '',
            'features': '',
            'createdBy': '',
            'createdAt': datetime.now(),
            'timeStamp': datetime.now()
        }

        try:
            self.conn = sqlite3.connect(self.db_name)
        except Error as e:
            print(e)

        with self.conn:
            create_table = '''CREATE TABLE IF NOT EXISTS {}
                (id         INTEGER PRIMARY KEY AUTOINCREMENT,
                 title      TEXT NOT NULL,
                 desc       TEXT DEFAULT "",
                 url        TEXT NOT NULL,
                 image      TEXT DEFAULT "",
                 siteName   TEXT NOT NULL,
                 features   TEXT DEFAULT "",
                 createdBy  TEXT NOT NULL,
                 createdAt  TEXT NOT NULL,
                 timeStamp  TEXT NOT NULL);'''.format(self.table_name)
            
            curs = self.conn.cursor()
            curs.execute(create_table)

        
    def insertTable(self, data):
        # 데이터 타입을 확인한다.
        assert type(data['title']) == str, 'title: type error'
        assert type(data['url']) == str, 'url: type error'
        assert type(data['siteName']) == str, 'siteName: type error'
        assert type(data['createdBy']) == str, 'createdBy: type error'
        assert type(data['createdAt']) == datetime, 'createdAt: type error'
        assert type(data['timeStamp']) == datetime, 'timeStamp: type error'
        # set data
        self.data['title'] = data['title']
        self.data['url'] = data['url']
        self.data['siteName'] = data['siteName']
        self.data['createdBy'] = data['createdBy']
        self.data['createdAt'] = data['createdAt']
        self.data['timeStamp'] = data['timeStamp']
        if data.get('desc'):
            self.data['desc'] = data['desc']
        if data.get('image'):
            self.data['image'] = data['image']
        if data.get('features'):
            self.data['features'] = data['features']
        # Insert data into Table
        # execute or push
        with self.conn:
            insert_table = """INSERT INTO {} 
                (title, desc, url, image, siteName, features, createdBy, createdAt, timeStamp) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(self.table_name)
            
            table_data = (self.data['title'], self.data['desc'], self.data['url'], 
                self.data['image'], self.data['siteName'], self.data['features'],
                data['createdBy'], data['createdAt'], data['timeStamp'])
            
            curs = self.conn.cursor()
            curs.execute(insert_table, table_data)

    def isNewItem(self, source, target):
        # Query title and return True if new data
        # select or equal_to
        with self.conn:
            query = 'SELECT * FROM {} WHERE {}=?'.format(self.table_name, source)
            curs = self.conn.cursor()
            curs.execute(query, (target,))
            if curs.fetchall():
                return False
            else:
                return True

    def close(self):
        # Commit and close database
        with self.conn:
            self.conn.commit()

        self.conn.close()

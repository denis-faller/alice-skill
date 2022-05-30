import json
import database_lib

connection = database_lib.createConnection("localhost", "root", "", 3307)
if True:
    createDatabaseQuery = "CREATE DATABASE skill_alice"
    database_lib.createDatabase(connection, createDatabaseQuery)
    useDatabaseQuery = "USE skill_alice"
    database_lib.useDatabase(connection, useDatabaseQuery)
    createTableQuery = """
    CREATE TABLE IF NOT EXISTS words (
        id int NOT NULL AUTO_INCREMENT,
        word varchar(255) NOT NULL,
        translations varchar(255) NOT NULL,
        status int,
        PRIMARY KEY (id)
    );
    """
    database_lib.createTable(connection, createTableQuery, "words")
    
    wordsDict = {
    0: {'word': 'pencil', 'tranlations': json.dumps(['карандаш', 'кисть'], ensure_ascii=False)},
    1: {'word': 'table', 'tranlations': json.dumps(['стол', 'таблица'], ensure_ascii=False)},
    2: {'word': 'girl', 'tranlations': json.dumps(['девушка', 'девочка'], ensure_ascii=False)},
    3: {'word': 'down', 'tranlations': json.dumps(['вниз', 'внизу'], ensure_ascii=False)},
    4: {'word': 'top', 'tranlations': json.dumps(['верх', 'верхний'], ensure_ascii=False)},
    5: {'word': 'read', 'tranlations': json.dumps(['читать', 'прочесть'], ensure_ascii=False)},
    6: {'word': 'help', 'tranlations': json.dumps(['помощь', 'помогать'], ensure_ascii=False)},
    7: {'word': 'love', 'tranlations': json.dumps(['любовь', 'любить'], ensure_ascii=False)},
    8: {'word': 'body', 'tranlations': json.dumps(['тело', ' корпус'], ensure_ascii=False)},
    9: {'word': 'go', 'tranlations': json.dumps(['идти', 'ехать'], ensure_ascii=False)},
    10: {'word': 'people', 'tranlations': json.dumps(['люди', 'народ'], ensure_ascii=False)}
    }
    
    i = 0
    for i in wordsDict:
        insertRowQuery = f"INSERT INTO words (id, word, translations, status) VALUES(0, '{wordsDict[i]['word']}', '{wordsDict[i]['tranlations']}', 0)"
        print (insertRowQuery)
        database_lib.insertRow(connection, insertRowQuery, "words")

if False:
    dropDatabaseQuery = "DROP DATABASE skill_alice"
    database_lib.dropDatabase(connection, dropDatabaseQuery)
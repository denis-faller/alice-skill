from flask import Flask
from flask import request
from translate import Translate
import json
import logging
import database_lib
import sys

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def main():
    global sessionCode, sessionID, trasnslateObjects

    # f = open('log.txt', "w+")
    # f.write(json.dumps(request.json))

    isState = False
    if 'state' in request.json.keys():
        if 'application' in request.json['state'].keys():
            if 'value' in request.json['state']['application'].keys():
                sessionCode = request.json['state']['application']['value']
                isState = True

    if not isState:
        sessionCode = request.json['session']['session_id']

    # f.write(sessionCode)
    # f.close()

    f = open('config.txt')
    config = []
    for line in f:
        config.append(line)

    connection = database_lib.createConnection(config[0], config[1], config[2].strip(), config[3])
    useDatabaseQuery = "USE skill_alice"
    database_lib.useDatabase(connection, useDatabaseQuery)

    selectQuery = "SELECT * FROM sessions WHERE code = '" + sessionCode + "'"
    session = database_lib.selectRows(connection, selectQuery)

    # f = open('log.txt', "w+")
    # f.write(str(session))
    # f.close()

    if len(session) == 0:
        insertRowQuery = f"INSERT INTO sessions (id, code) VALUES(0, '{sessionCode}')"
        database_lib.insertRow(connection, insertRowQuery, "sessions")

        selectQuery = "SELECT * FROM sessions WHERE code = '" + sessionCode + "'"
        session = database_lib.selectRows(connection, selectQuery)

        sessionID = session[0][0]

        # f = open('log.txt', "w+")
        # f.write(str(session[0][0]))
        # f.close()

        wordsDict = {
            0: {'word': 'pencil', 'tranlations': json.dumps(['карандаш', 'кисть'], ensure_ascii=False), 'status': 2},
            1: {'word': 'table', 'tranlations': json.dumps(['стол', 'таблица'], ensure_ascii=False), 'status': 2},
            2: {'word': 'girl', 'tranlations': json.dumps(['девушка', 'девочка'], ensure_ascii=False), 'status': 2},
            3: {'word': 'down', 'tranlations': json.dumps(['вниз', 'внизу'], ensure_ascii=False), 'status': 2},
            4: {'word': 'top', 'tranlations': json.dumps(['верх', 'верхний'], ensure_ascii=False), 'status': 2},
            5: {'word': 'read', 'tranlations': json.dumps(['читать', 'прочесть'], ensure_ascii=False), 'status': 2},
            6: {'word': 'help', 'tranlations': json.dumps(['помощь', 'помогать'], ensure_ascii=False), 'status': 2},
            7: {'word': 'love', 'tranlations': json.dumps(['любовь', 'любить'], ensure_ascii=False), 'status': 2},
            8: {'word': 'body', 'tranlations': json.dumps(['тело', ' корпус'], ensure_ascii=False), 'status': 2},
            9: {'word': 'go', 'tranlations': json.dumps(['идти', 'ехать'], ensure_ascii=False), 'status': 2},
            10: {'word': 'people', 'tranlations': json.dumps(['люди', 'народ'], ensure_ascii=False), 'status': 2}
        }

        i = 0
        for i in wordsDict:
            insertRowQuery = f"INSERT INTO words (id, word, translations, status, id_session) VALUES(0, '{wordsDict[i]['word']}', '{wordsDict[i]['tranlations']}', '{wordsDict[i]['status']}', '{sessionID}')"
            database_lib.insertRow(connection, insertRowQuery, "words")
    else:
        selectQuery = "SELECT * FROM sessions WHERE code = '" + sessionCode + "'"
        session = database_lib.selectRows(connection, selectQuery)

        sessionID = session[0][0]

    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    if trasnslateObjects == 0:
        trasnslateObjects = {sessionID: Translate()}
    elif sessionID not in trasnslateObjects.keys():
        trasnslateObjects[sessionID] = Translate()

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        },
        "application_state": {
            "value": sessionCode
        },
    }

    handleDialog(response, request.json)

    if trasnslateObjects[sessionID].isAnswer:
        buttons = [
            {
                "title": "завершить",
                "payload": {"end": 1},
                "hide": True,
            },
            {
                "title": "да",
                "payload": {"yes": 1},
                "hide": True,
            },
            {
                "title": "нет",
                "payload": {"no": 1},
                "hide": True,
            }
        ]
    else:
        buttons = [
            {
                "title": "завершить",
                "payload": {"end": 1},
                "hide": True,
            }
        ]
    response['response']['buttons'] = buttons

    return json.dumps(response)


connection = 0
LIMIT_WORDS = 11
sessionsLimit = 0
trasnslateObjects = 0
sessionCode = ""
sessionID = 0

def getWords():
    global connection, LIMIT_WORDS, trasnslateObjects, sessionID

    f = open('config.txt')
    config = []
    for line in f:
        config.append(line)
    connection = database_lib.createConnection(config[0], config[1], config[2].strip(), config[3])
    useDatabaseQuery = "USE skill_alice"
    database_lib.useDatabase(connection, useDatabaseQuery)

    selectQuery = "SELECT * FROM words WHERE status = 2 AND id_session = " + str(sessionID) + " LIMIT " + str(LIMIT_WORDS - 1)
    trasnslateObjects[sessionID].words = database_lib.selectRows(connection, selectQuery)
    lenInCorrectWords = len(trasnslateObjects[sessionID].words)

    selectQuery = "SELECT * FROM words WHERE status = 0 AND id_session = " + str(sessionID) + " LIMIT " + str(LIMIT_WORDS - lenInCorrectWords - 1)

    # f = open('log.txt', "w+")
    # f.write(selectQuery)
    # f.close()

    trasnslateObjects[sessionID].words.extend(database_lib.selectRows(connection, selectQuery))
    # logging.error('%s raised an error',  words)


def getWord():
    global trasnslateObjects, sessionID

    # logging.error('%s words',  words)
    trasnslateObjects[sessionID].idCurWord = trasnslateObjects[sessionID].words[0][0]
    trasnslateObjects[sessionID].curWord = trasnslateObjects[sessionID].words[0][1]
    if len(trasnslateObjects[sessionID].words) > 1:
        trasnslateObjects[sessionID].nextWord = trasnslateObjects[sessionID].words[1][1]
    else:
        trasnslateObjects[sessionID].nextWord = trasnslateObjects[sessionID].words[0][1]
    trasnslateObjects[sessionID].translationOptions = trasnslateObjects[sessionID].words[0][2]
    trasnslateObjects[sessionID].translationOptions = trasnslateObjects[sessionID].translationOptions.replace("[",
                                                                                                              "").replace(
        "]", "").replace('"', "").replace("'", "").replace(" ", "").replace("'", "").split(",")
    trasnslateObjects[sessionID].words.pop(0)
    return [trasnslateObjects[sessionID].idCurWord, trasnslateObjects[sessionID].nextWord,
            trasnslateObjects[sessionID].translationOptions]


def resultAnswer(res, requestText):
    global connection, sessionsLimit, sessionID, trasnslateObjects

    isHasInTranslationOptions = False
    for wordItem in trasnslateObjects[sessionID].translationOptions:
        # logging.error('%s raised an error',  wordItem)
        # logging.error('%s raised an error',  wordItem == requestText)
        if wordItem == requestText:
            isHasInTranslationOptions = True

    correctAnswer = trasnslateObjects[sessionID].translationOptions[0]

    # logging.error('%s translationOptions', translationOptions)
    # logging.error('%s cntWords',  cntWords)
    # logging.error('%s sessionLimit',  sessionLimit)
    # logging.error('%s len',  len(words))
    if (isHasInTranslationOptions) and (requestText != ""):
        if trasnslateObjects[sessionID].cntWords == (sessionsLimit[sessionID] - 1):
            res['response']['text'] = "Правильно. Будем продолжать?\n"
            trasnslateObjects[sessionID].isAnswer = True
        elif len(trasnslateObjects[sessionID].words) == 0:
            res['response']['text'] = "Правильно. Слов для изучения нет\n"
        else:
            res['response']['text'] = "Правильно.\nПереведи слово - " + trasnslateObjects[sessionID].nextWord
        updateRowQuery = f"UPDATE words SET status = 1 WHERE id = " + str(trasnslateObjects[sessionID].idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")
    else:
        if trasnslateObjects[sessionID].cntWords == (sessionsLimit[sessionID] - 1):
            res['response']['text'] = "Неправильно. Правильно {0}. Будем продолжать?\n".format(correctAnswer)
            trasnslateObjects[sessionID].isAnswer = True
        elif len(trasnslateObjects[sessionID].words) == 0:
            res['response']['text'] = "Неправильно. Правильно {0}. Слов для изучения нет\n".format(correctAnswer)
        else:
            res['response']['text'] = "Неправильно. Правильно {0}. Переведи слово - {1}".format(correctAnswer,
                                                                                                trasnslateObjects[
                                                                                                    sessionID].nextWord)
        # logging.error('%s idCurWord',  idCurWord)
        updateRowQuery = f"UPDATE words SET status = 2 WHERE id = " + str(trasnslateObjects[sessionID].idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")
        trasnslateObjects[sessionID].words.append((trasnslateObjects[sessionID].idCurWord,
                                                   trasnslateObjects[sessionID].curWord,
                                                   str(trasnslateObjects[sessionID].translationOptions)))
        sessionsLimit[sessionID] += 1
    if trasnslateObjects[sessionID].cntWords != (sessionsLimit[sessionID] - 1):
        if len(trasnslateObjects[sessionID].words) != 0:
            listWord = getWord()
            trasnslateObjects[sessionID].idCurWord = listWord[0]
            trasnslateObjects[sessionID].nextWord = listWord[1]
            trasnslateObjects[sessionID].translationOptions = listWord[2]
    elif len(trasnslateObjects[sessionID].words) != 0:
        trasnslateObjects[sessionID].words.pop(0)


def handleDialog(res, req):
    global trasnslateObjects, LIMIT_WORDS, sessionID, sessionsLimit

    requestText =  ""
    if 'original_utterance' in req['request']:
        requestText = req['request']['original_utterance'].lower()
    elif 'payload' in req['request']:
        if 'end' in req['request']['payload']:
            requestText = "завершить"
        elif 'no' in req['request']['payload']:
            requestText = "нет"
        elif 'yes' in req['request']['payload']:
            requestText = "да"

    # f = open('log.txt', "w+")
    # f.write(str(req))
    # f.close()

    # logging.error('%s words', words)
    if trasnslateObjects[sessionID].cntWords > 0:
        if requestText == "завершить":
            res['response']['text'] = "Отлично. Если будет скучно, потренируйся"
        else:
            # logging.error('%s cntWords', cntWords)
            if sessionsLimit == 0:
                sessionsLimit = {sessionID: LIMIT_WORDS}
            elif sessionID not in sessionsLimit.keys():
                sessionsLimit[sessionID] = LIMIT_WORDS
            if trasnslateObjects[sessionID].cntWords == sessionsLimit[sessionID]:
                if requestText == "нет":
                    trasnslateObjects[sessionID].isAnswer = False
                    res['response']['text'] = "Отлично потренировались. Не забывай повторять"
                else:
                    trasnslateObjects[sessionID].isAnswer = False
                    getWords()
                    if len(trasnslateObjects[sessionID].words) == 0:
                        res['response']['text'] = "Слов для изучения нет"
                        return
                    listWord = getWord()
                    trasnslateObjects[sessionID].idCurWord = listWord[0]
                    trasnslateObjects[sessionID].nextWord = listWord[1]
                    trasnslateObjects[sessionID].translationOptions = listWord[2]
                    res['response']['text'] = "Продолжаем.\nПереведи слово - " + trasnslateObjects[sessionID].nextWord
                    trasnslateObjects[sessionID].cntWords = 1
            elif trasnslateObjects[sessionID].cntWords < sessionsLimit[sessionID]:
                # logging.error('%s raised an error', words[wordIndex][1])
                # logging.error('%s raised an error', words[wordIndex - 1])
                # logging.error('%s raised an error', wordIndex)
                resultAnswer(res, requestText)
                trasnslateObjects[sessionID].cntWords += 1
    else:
        getWords()
        # logging.error('%s raised an error', words)
        if len(trasnslateObjects[sessionID].words) == 0:
            res['response']['text'] = "Слов для изучения нет"
            return
        trasnslateObjects[sessionID].nextWord = trasnslateObjects[sessionID].words[0][1]
        res['response']['text'] = "Здравствуй. Давай начнем учить английский вместе со мной.\nПереведи слово - " + \
                                  trasnslateObjects[sessionID].nextWord
        listWord = getWord()
        trasnslateObjects[sessionID].idCurWord = listWord[0]
        trasnslateObjects[sessionID].nextWord = listWord[1]
        trasnslateObjects[sessionID].translationOptions = listWord[2]
        trasnslateObjects[sessionID].cntWords += 1


if __name__ == '__main__':
    app.run()
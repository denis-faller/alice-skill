from flask import Flask
from flask import request
import json
import logging
import database_lib

app = Flask(__name__)

@app.route('/post', methods=['POST'])
# Логика взаимодействия между сессиями
def main():
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        },
    }
    handleDialog(response, request.json)
    return json.dumps(response)

connection = 0
cntWords = 0
words = []
idCurWord = 0
nextWord = ""
translationOptions = ""
LIMIT_WORDS = 10

def getWords():
    global connection, words, LIMIT_WORDS
    connection = database_lib.createConnection("localhost", "root", "", 3307)
    useDatabaseQuery = "USE skill_alice"
    database_lib.useDatabase(connection, useDatabaseQuery)
    selectQuery = "SELECT * FROM words WHERE status = 0 LIMIT " + str(LIMIT_WORDS)
    words = database_lib.selectRows(connection, selectQuery)
    logging.error('%s raised an error',  words)

# Логика правильно/неправильно (если неправильно то выводить правильные варианты, повтор в конце)
# Выборка (неправильные 50%, новые 50%)
def getWord():
    global cntWords, words
    idCurWord = words[0][0]
    translationOptions = words[0][2]
    translationOptions = translationOptions.replace("[", "").replace("]", "").replace('"', "").replace(" ", "").split(",")
    if cntWords == 1:
        words.pop(0)
    nextWord = words[1][1]
    if cntWords != 0:
        words.pop(0)
    else:
        idCurWord = words[0][0]
    return [idCurWord, nextWord, translationOptions]
    
def resultAnswer(res, requestText):
    global connection, words, idCurWord, nextWord, translationOptions
    
    #logging.error('%s raised an False', idCurWord)    
 
    if len(words) == 0:
        updateRowQuery = f"UPDATE words SET status = 2 WHERE id = " + str(idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")
        res['response']['text'] = "Слов для изучения больше нет"
        return      
    
    #logging.error('%s raised an error',  requestText)
    #logging.error('%s raised an error',  word[2])
    #logging.error('%s raised an error',  wordIndex)
        
    #logging.error('%s raised an error',  wordIndex)
        
    #logging.error('%s raised an error',  idCurWord)
    #logging.error('%s raised an error',  translationOptions)
    isHasInTranslationOptions = False
    for wordItem in translationOptions:
        #logging.error('%s raised an error',  wordItem)
        #logging.error('%s raised an error',  wordItem == requestText)
        if wordItem == requestText:
            isHasInTranslationOptions = True
    
    if (isHasInTranslationOptions) and (requestText != ""):
        res['response']['text'] = "Правильно.\nПереведи слово - " + nextWord
        updateRowQuery = f"UPDATE words SET status = 1 WHERE id = " + str(idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")
    else:
        res['response']['text'] = "Неправильно.\nПереведи слово - " + nextWord
        updateRowQuery = f"UPDATE words SET status = 2 WHERE id = " + str(idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")
    if len(words) != 0:
        listWord = getWord()
        idCurWord = listWord[0]
        nextWord = listWord[1]
        translationOptions = listWord[2]
    else:
        updateRowQuery = f"UPDATE words SET status = 2 WHERE id = " + str(idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")

# Логика правильно/неправильно (если неправильно то выводить правильные варианты, повтор в конце)
# Добавить кнопку завершить, повторить
def handleDialog(res, req):
    global cntWords, words, idCurWord, nextWord, LIMIT_WORDS
    requestText = req['request']['original_utterance'].lower()
    
    if cntWords > 0:
        if requestText == "завершить":
            res['response']['text'] = "Отлично. Если будет скучно, потренируйся"
            cntWords = 0
        else:
            if  cntWords == LIMIT_WORDS:
                # Добавить кнопки да/нет
                if requestText == "нет":
                    res['response']['text'] = "Отлично потренировались. Не забывай повторять"
                elif requestText != "да":
                    res['response']['text'] = "Будем продолжать?"
                else:
                    getWords()
                    #logging.error('%s raised an error',  words)
                    if len(words) == 0:
                        res['response']['text'] = "Слов для изучения больше нет"
                        return
                    curWord = words[0][1]
                    res['response']['text'] = "Продолжаем.\nПереведи слово - " + curWord
                    cntWords = 1
            elif cntWords < LIMIT_WORDS + 1:
                #logging.error('%s raised an error', words[wordIndex][1])
                #logging.error('%s raised an error', words[wordIndex - 1])
                #logging.error('%s raised an error', wordIndex)
                resultAnswer(res, requestText)
                cntWords+= 1
    else:
        getWords()
        #logging.error('%s raised an error', words)
        if len(words) == 0:
            res['response']['text'] = "Слов для изучения нет"
            return
        nextWord = words[0][1]
        res['response']['text'] = "Здравствуй. Давай начнем учить английский вместе со мной.\nПереведи слово - " + nextWord
        listWord = getWord()
        idCurWord = listWord[0]
        nextWord = listWord[1]
        translationOptions = listWord[2]
        # Добавить условие выше
        cntWords+= 1

if __name__ == '__main__':
    app.run()
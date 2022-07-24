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
curWord = ""
nextWord = ""
translationOptions = ""
LIMIT_WORDS = 11
sessionLimit = LIMIT_WORDS

# Выборка (неправильные 50%, новые 50%)
def getWords():
    global connection, words, LIMIT_WORDS
    f = open('config.txt')
    config = []
    for line in f:
        config.append(line)
    connection = database_lib.createConnection(config[0], config[1], config[2].strip(), config[3])
    useDatabaseQuery = "USE skill_alice"
    database_lib.useDatabase(connection, useDatabaseQuery)
    selectQuery = "SELECT * FROM words WHERE status = 0 LIMIT " + str(LIMIT_WORDS - 1)
    words = database_lib.selectRows(connection, selectQuery)
    #logging.error('%s raised an error',  words)

def getWord():
    global cntWords, words, idCurWord, curWord, nextWord, translationOptions
    #logging.error('%s words',  words)
    idCurWord = words[0][0]
    curWord = words[0][1] 
    if len(words) > 1:
        nextWord = words[1][1] 
    else:
        nextWord = words[0][1] 
    translationOptions = words[0][2]
    translationOptions = translationOptions.replace("[", "").replace("]", "").replace('"', "").replace("'", "").replace(" ", "").replace("'", "").split(",")
    words.pop(0)
    return [idCurWord, nextWord, translationOptions]
    
def resultAnswer(res, requestText):
    global connection, words, idCurWord, curWord, nextWord, translationOptions, sessionLimit
    
    isHasInTranslationOptions = False
    for wordItem in translationOptions:
        #logging.error('%s raised an error',  wordItem)
        #logging.error('%s raised an error',  wordItem == requestText)
        if wordItem == requestText:
            isHasInTranslationOptions = True
            
    correctAnswer = translationOptions[0]        
    
    logging.error('%s translationOptions', translationOptions)
    logging.error('%s cntWords',  cntWords)
    logging.error('%s sessionLimit',  sessionLimit)
    #logging.error('%s len',  len(words))
    if (isHasInTranslationOptions) and (requestText != ""):
        if cntWords == (sessionLimit - 1):
            res['response']['text'] = "Правильно. Будем продолжать?\n"
        elif len(words) == 0:
            res['response']['text'] = "Правильно. Слов для изучения нет\n"    
        else:
            res['response']['text'] = "Правильно.\nПереведи слово - " + nextWord
        updateRowQuery = f"UPDATE words SET status = 1 WHERE id = " + str(idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")
    else:
        if cntWords == (sessionLimit - 1):
            res['response']['text'] = "Неправильно. Правильно {0}. Будем продолжать?\n".format(correctAnswer)
        elif len(words) == 0:
            res['response']['text'] = "Неправильно. Правильно {0}. Слов для изучения нет\n".format(correctAnswer)
        else:
            res['response']['text'] = "Неправильно. Правильно {0}. Переведи слово - {1}".format(correctAnswer, nextWord)
        #logging.error('%s idCurWord',  idCurWord)    
        updateRowQuery = f"UPDATE words SET status = 2 WHERE id = " + str(idCurWord)
        database_lib.updateRow(connection, updateRowQuery, "words")
        words.append((idCurWord, curWord, "{0}".format(translationOptions)))
        sessionLimit +=1
    if cntWords != (sessionLimit - 1):
        if len(words) != 0:
            listWord = getWord()
            idCurWord = listWord[0]
            nextWord = listWord[1]
            translationOptions = listWord[2]
    elif len(words) != 0:
        words.pop(0)

# Логика правильно/неправильно (если неправильно то выводить правильные варианты, повтор в конце)
# Добавить кнопку завершить, да-нет
def handleDialog(res, req):
    global cntWords, words, idCurWord, nextWord, translationOptions, LIMIT_WORDS, sessionLimit
    requestText = req['request']['original_utterance'].lower()
    
    logging.error('%s words', words)
    if cntWords > 0:
        if requestText == "завершить":
            res['response']['text'] = "Отлично. Если будет скучно, потренируйся"
        else:
            #logging.error('%s cntWords', cntWords)
            if  cntWords == sessionLimit:
                if requestText == "нет":
                    res['response']['text'] = "Отлично потренировались. Не забывай повторять"
                else:
                    getWords()
                    if len(words) == 0:
                        res['response']['text'] = "Слов для изучения нет"
                        return
                    listWord = getWord()
                    idCurWord = listWord[0]
                    nextWord = listWord[1]
                    translationOptions = listWord[2]
                    res['response']['text'] = "Продолжаем.\nПереведи слово - " + nextWord
                    cntWords = 1
                    sessionLimit = LIMIT_WORDS
            elif cntWords < sessionLimit:
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
        cntWords+= 1

if __name__ == '__main__':
    app.run()
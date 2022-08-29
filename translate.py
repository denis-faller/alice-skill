class Translate:
    cntWords = 0
    words = []
    idCurWord = 0
    curWord = ""
    nextWord = ""
    translationOptions = ""

    def __str__(self):
        return f"cntWords: {self.cntWords}  words: {self.words} idCurWord: {self.idCurWord} curWord: {self.curWord} nextWord: {self.nextWord} translationOptions: {self.translationOptions}"
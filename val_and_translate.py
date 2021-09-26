import re
from enchant.checker import SpellChecker
import enchant
import translators as ts


kirill = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

            
def word_validator_and_traslator(text: str,):

    '''this function parses input, if iunput is valid, translate the word or phrase
    and returs it, otherwise returns a warning in the form of a string '''

    text = text.strip().lower()
    if re.match(r'[а-яё]', text[0]):
        lang = 'ru_RU'
    elif re.match(r'[a-z]', text[0]):
        lang = 'en_US'
    else:
        return 'А word or phrase must begin with a letter.'    
    chkr = SpellChecker(lang)
    chkr.set_text(text)
    list_err = []
    for err in chkr:
        list_err.append(err.word)
    if len(list_err) == 1:
        d = enchant.Dict("en_US")
        sugg = d.suggest(list_err[0])
        if sugg:
            return f"Unknown word - {list_err[0]}.\nTry some of this: {', '.join(sugg)}"
        return f"Unknown word - {list_err[0]}"
    elif len(list_err) > 1:
        return f"Unknown words - {', '.join(list_err)}."  
    if lang == 'ru_RU':
        try:
            translate = ts.google(text, from_language='ru', to_language='en').lower()
            return text, translate 
        except:
            return 'The translation failed.'      
    elif lang == 'en_US':
        try:
            translate = ts.google(text, from_language='en', to_language='ru').lower() 
            return translate, text
        except:
            return 'The translation failed.'

import requests
from bs4 import BeautifulSoup



def get_irregular_verbs():
    URL = 'http://www.broadway.kiev.ua/faq2.html'
    response = requests.get(URL).text
    soup = BeautifulSoup(response, 'lxml')
    list_rows = []
    for row in soup.find_all('tr'):
        list_words = []
        for word in row.find_all('td'):
            list_words.append(word.text)
        list_rows.append(list_words)   
    return list_rows[1:]
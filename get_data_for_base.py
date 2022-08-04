import requests
from bs4 import BeautifulSoup


def get_irregular_verbs():
    URL = "http://www.broadway.kiev.ua/faq2.html"
    response = requests.get(URL).text
    soup = BeautifulSoup(response, "lxml")
    list_rows = []
    for row in soup.find_all("tr"):
        list_words = []
        for word in row.find_all("td"):
            list_words.append(word.text)
        list_rows.append(list_words)
    return list_rows[1:]


def get_gerund_or_inf():
    URL = "https://www.engvid.com/english-resource/verbs-followed-by-gerunds-and-infinitives/"
    response = requests.get(URL).text
    soup = BeautifulSoup(response, "lxml")
    g_l = []
    for ul in soup.find_all("ul", class_="wordlist"):
        sublist = []
        for li in ul.find_all("li"):
            sublist.append(li.text)
        g_l.append(sublist)
    result_list = [g_l[0] + g_l[1] + g_l[2], g_l[3] + g_l[4] + g_l[5], g_l[6]]
    return result_list

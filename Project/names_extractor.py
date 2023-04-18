import requests
import csv
import unicodedata

def get_wikipedia_article_text(title, language='en'):
    base_url = f'https://{language}.wikipedia.org/w/api.php'

    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'exlimit': '1',
        'explaintext': '1',
        'titles': title
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    page_id = list(data['query']['pages'].keys())[0]

    if page_id == '-1':
        print('Article not found.')
        return None

    text = data['query']['pages'][page_id]['extract']
    return text

def extract_id(string, type):
    start = string.rfind("/") + 1
    if type == "int":
        end = string.find('.jpg')
        return int(string[start:end])
    elif type == "csv":
        end = string.find('.csv')
        return str(string[start:end])

def extract_name(string):
    start = 0
    # end = -1
    end = string.find('–')
    if end == -1:
        end = string.find('--')
        if end == -1:
            end = string.find('- ')

    return str(string[start:end-1])

def remove_title(string):
    if "," in string:
        start = 0
        end = string.find(',')
        return str(string[start:end])
    else:
        return string

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    no_accent = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    no_accent = no_accent.replace('ø', 'o').replace('Ø', 'O').replace('œ', 'oe').replace('Œ', 'Oe')
    return no_accent

outliers = ["Vania Jordanova", "Antal Istvan Jakli"]
def clean_name(string):
    string = remove_accents(string)
    string = extract_name(string)
    string = remove_title(string)
    string = string.encode('utf-8').decode('unicode-escape')

    for outlier in outliers:
        if outlier in string:
            string = outlier
    if string == "Charlotte (nee Riefenstahl) Houtermans":
        return "Charlotte Houtermans"
    return string

def clean_article(text):
    text_list = text.splitlines(True)
    text_list = [s.replace("\n", "") for s in text_list]
    text_list = [s for s in text_list if "=" not in s]
    text_list = list(filter(None, text_list))

    text_list = text_list[1:]
    text_list = text_list[:-3]

    text_list = [clean_name(s) for s in text_list]
    print(text_list)
    with open('output.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for string in text_list:
            writer.writerow([string])
    return text_list
article_title = 'List_of_physicists'
article_text = get_wikipedia_article_text(article_title)

print(clean_article(article_text))
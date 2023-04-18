import requests
import csv
import re
import unicodedata

import wikipedia

def clean_gpt_csv(gpt_file):
    names_dict = {}

    # Open the CSV file
    "influencers_and_influenced_names.csv"
    with open(gpt_file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Extract the names from the 'to' column using regular expression
            raw_to_names = re.findall('\d+\.\s(\w+\s?\w+)', row['to'])
            clean_to_names = []
            for raw_name in raw_to_names:
                clean_to_names.append(raw_name.lower())
            # Create a dictionary entry with the 'from' column as the key and the 'to' names as the value
            raw_from_name = row['from']
            clean_from_name = raw_from_name.lower().replace("_", " ")
            names_dict[clean_from_name] = clean_to_names

    print(len(names_dict))
    print(names_dict)

    return names_dict

clean_gpt_csv("influencers_and_influenced_names.csv")

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
specific_outliers = ["Abu_Rayhan_Al-biruni"]

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
    if string == "Pu (Paul) Wang":
        return "Wang Pu (physicist)"
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

    text_list = [s for s in text_list if "Abdulla Majed" not in s]

    with open('output.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for string in text_list:
            writer.writerow([string])
    return text_list

# article_title = 'List_of_physicists'

# article_text = get_wikipedia_article_text(article_title)
# text_list = clean_article(article_text)
# results_list = []
# for name in text_list:
#     results_list.append(wikipedia.search(name)[0])
#
# print(results_list)


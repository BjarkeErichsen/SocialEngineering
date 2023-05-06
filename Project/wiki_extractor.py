import requests
from tqdm import tqdm
import json
import wikipedia
import requests
from bs4 import BeautifulSoup
import pickle
from urllib.parse import urlparse
import multiprocessing as mp
import re

from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

countries =  ['United States (U.S.A)', 'United Kingdom (U.K.)', 'Germany', 'France', 'Japan', 'Russia (USSR)',
              'Canada', 'Italy', 'Switzerland', 'Sweden', 'Australia', 'Netherlands', 'China',
              'South Korea', 'Israel', 'Denmark', 'Spain', 'Belgium', 'Austria', 'Norway',
              'Finland', 'India', 'Brazil', 'Mexico', 'Poland', 'Turkey', 'Czech Republic',
              'Portugal', 'Greece', 'Hungary', 'Ireland', 'Taiwan', 'Argentina', 'Romania',
              'Serbia', 'Singapore', 'Croatia', 'Slovenia', 'Ukraine', 'New Zealand', 'Bulgaria',
              'Egypt', 'Iran', 'Jordan', 'Kazakhstan', 'Malaysia', 'Morocco', 'Saudi Arabia',
              'South Africa', 'Thailand', 'Tunisia', 'Vietnam', 'Bangladesh', 'Chile', 'Colombia',
              'Indonesia', 'Kenya', 'Nigeria', 'Pakistan', 'Peru']
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

def save_dict_txt(dictionary_to_save, text_name):
    with open(text_name, 'w', encoding='utf-8') as file:
        json.dump(dictionary_to_save, file, ensure_ascii=False)

def load_dict_txt(input_txt):
    with open(input_txt, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    id_to_name_dict = {}
    for line in lines:
        key, value = line.strip().split(',', 1)
        id_to_name_dict[key] = value

    return id_to_name_dict

def load_dict_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        my_dict = json.load(file)
    return my_dict

def find_wiki_page_id(title):
    url = "https://en.wikipedia.org/w/api.php"
    session = requests.Session()
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "info"
    }
    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the pageid value from the response
    pageid = next(iter(data["query"]["pages"])).split()[0]
    return pageid

def find_wiki_title_from_id(pageid):

    if pageid ==  '-1':
        return "Non existing page (Pageid = -1)"
    # Specify the Wikipedia API endpoint and parameters
    wiki_api_endpoint = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "info",
        "format": "json",
        "pageids": pageid
    }

    # Make a GET request to the Wikipedia API
    response = requests.get(wiki_api_endpoint, params=params)

    # Parse the JSON response to retrieve the page title
    page_data = response.json()["query"]["pages"][pageid]
    page_title = page_data["title"]
    return page_title

def find_wiki_page_id_from_url(url):
    parsed_url = urlparse(url)
    title = parsed_url.path.split("/")[-1]
    api_url = f"https://{parsed_url.netloc}/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "info"
    }
    # Make the API request
    response = requests.get(api_url, params=params)
    data = response.json()

    # Extract the pageid value from the response
    pageid = next(iter(data["query"]["pages"])).split()[0]
    return pageid

def count_occurrences(lst):
    counts = {}
    for elem in lst:
        if elem in counts:
            counts[elem] += 1
        else:
            counts[elem] = 1
    return [(elem, counts[elem]) for elem in counts]

def get_birth_year(sentence):
    birth_year = None

    # match for format like "YYYY–YYYY"
    match = re.search(r"\((\d{4})[\u2013-](\d{4})\)", sentence)
    if match:
        birth_year = int(match.group(1))

    # match for format like "born YYYY"
    if not birth_year:
        match = re.search(r"born (\d{4})", sentence)
        if match:
            birth_year = int(match.group(1))

    # match for format like "ca. YYYY-YYYY BC"
    if not birth_year:
        match = re.search(r"ca\. (\d{4})[\u2013-](\d{4}) BC", sentence)
        if match:
            birth_year = -int(match.group(1))

    # match for format like "YYYY–YYYY Nobel laureate"
    if not birth_year:
        match = re.search(r"(\d{4})[\u2013-](\d{4}) Nobel", sentence)
        if match:
            birth_year = int(match.group(1))

    return birth_year

def extract_country(string):

    end = string.find('(')
    if end == -1:
        end = None
    start = string.find('–')
    if start == -1:
        start = string.find('--')
        if start == -1:
            start = string.find('- ')
            if start == -1:
                start = 0
    return str(string[start+2:end]), start, end
def generate_embedding_list(list):
    embedding_list = []
    for i in list:
        embedding_i = model.encode(i)
        embedding_list.append(embedding_i)
    return embedding_list

def find_most_similar(subject, embedding_list):
    embedding_subject = model.encode(subject)
    most_similar = None
    max_score = 0
    for e, embedding in enumerate(embedding_list):
        similarity = cosine_similarity([embedding_subject], [embedding])
        if similarity>max_score:
            max_score = similarity
            most_similar = e
    return most_similar

def extract_names_from_list():
    # Specify the URL and parameters for the API request
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": "List of physicists",
        "prop": "links",
    }

    # Make the API request
    response = requests.get(url, params=params)

    # Extract the links from the API response
    title_list = []

    article_title = 'List_of_physicists'
    article_text = get_wikipedia_article_text(article_title)
    text_list = article_text.splitlines(True)
    text_list = [s.replace("\n", "") for s in text_list]
    text_list = [s for s in text_list if "=" not in s]
    text_list = list(filter(None, text_list))
    text_list = text_list[1:]
    text_list = text_list[:-3]

    embedding_list_wiki = generate_embedding_list(text_list)
    embedding_list_countries = generate_embedding_list(countries)

    if response.status_code == 200:
        data = response.json()

        if "links" in data["parse"]:
            for link in tqdm(data["parse"]["links"]):
                link_title = link["*"]
                link_params = {
                    "action": "query",
                    "format": "json",
                    "titles": link_title,
                    "prop": "categories",
                }
                link_response = requests.get(url, params=link_params)
                if link_response.status_code == 200:
                    link_data = link_response.json()
                    data_json = link_data["query"]["pages"]
                    pageid = next(iter(data_json))
                    title = data_json[pageid]['title']

                    most_similar_line_in_wiki_id = find_most_similar(title,embedding_list_wiki)
                    most_similar_line_in_wiki = text_list[most_similar_line_in_wiki_id]
                    country_estimate = extract_country(most_similar_line_in_wiki)[0]
                    birth_year = get_birth_year(most_similar_line_in_wiki)
                    if country_estimate in countries:
                        title_list.append((pageid, title, country_estimate, birth_year))

                    else:
                        most_similar_country_id = find_most_similar(country_estimate, embedding_list_countries)
                        most_similar_country = countries[most_similar_country_id]
                        title_list.append((pageid, title, most_similar_country, birth_year))


    with open('titles_ids.txt', 'w', encoding='utf-8') as f:
        for pageid, title, country, birth_year in title_list:
            if pageid != -1:
                f.write(f"{pageid},{title},{country}, {birth_year}\n")

def get_physicist_social_network(name, base_url, id_to_name_dict, list_valid_ids):
    title_list = []

    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": name,
        "prop": "text",
        "redirects": 1,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        html = data["parse"]["text"]["*"]

        soup = BeautifulSoup(html, 'html.parser')

        # Remove navboxes
        for navbox in soup.find_all('div', {'class': 'navbox'}):
            navbox.decompose()

        # Extract links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/wiki/'):
                full_url = f'{base_url}{href}'
                page_id = find_wiki_page_id_from_url(full_url)
                if page_id in list_valid_ids:

                    linked_physicist = id_to_name_dict[page_id]

                    title_list.append(linked_physicist)

    except Exception as e:
        print(f"Error processing {name}: {e}")

    return (name, count_occurrences(title_list))

def the_social_network(input_txt, output_txt):
    influence_dict = {}
    id_to_name_dict = load_dict_txt(input_txt)
    name_to_id_dict = {value: key for key, value in id_to_name_dict.items()}

    save_dict_txt(id_to_name_dict, "id_to_name_dict.txt")
    save_dict_txt(name_to_id_dict, "name_to_id_dict.txt")

    base_url = 'https://en.wikipedia.org'
    list_valid_ids = set(id_to_name_dict.keys())

    with mp.Pool() as pool:
        results = []
        for physicist_name in id_to_name_dict.values():
            results.append(pool.apply_async(get_physicist_social_network,
                                            (physicist_name, base_url, id_to_name_dict, list_valid_ids)))

        for result in tqdm(results):
            name, title_list = result.get()
            influence_dict[name] = title_list

    # Save the dictionary as a JSON string to the text file
    save_dict_txt(influence_dict, "social_network.txt")

    with open(output_txt, 'w', encoding='utf-8') as file:
        json.dump(influence_dict, file, ensure_ascii=False)

if __name__ == '__main__':
    # the_social_network("real_titles_ids.txt", "social_network.txt")
    # social_network = load_dict_json("social_network.txt")
    # print(social_network)

    model = SentenceTransformer('sentence-transformers/paraphrase-distilroberta-base-v1')

    extract_names_from_list()
    max_score = 0
    most_similar_country = None



    # print(most_similar_country)
    # print(similarity)



import requests
from tqdm import tqdm
import json
import wikipedia
import requests
from bs4 import BeautifulSoup


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
                    title_list.append((pageid, title))

    with open('titles_ids.txt', 'w', encoding='utf-8') as f:
        for pageid, title in title_list:
            if pageid != -1:
                f.write(f"{pageid},{title}\n")

# extract_names_from_list()

def the_social_network(input_txt, output_txt):
    influence_dict = {}

    id_to_name_dict = load_dict_txt(input_txt)
    name_to_id_dict = {value: key for key, value in id_to_name_dict.items()}

    save_dict_txt(id_to_name_dict, "id_to_name_dict.txt")
    save_dict_txt(name_to_id_dict, "name_to_id_dict.txt")

    list_valid_ids = id_to_name_dict.keys()

    for physicist_name in tqdm(id_to_name_dict.values()):
        physicist_id = name_to_id_dict[physicist_name]
        title_list = []

        # if len(influence_dict)>50:
        #     break
        # #simpler code:

        # links_on_page = wikipedia.page(physicist_name).links
        # for link in links_on_page:
        #     try:
        #         page_id = name_to_id_dict[link]
        #         print("link found:   ", page_id, link)
        #         title_list.append((page_id, link))
        #     except KeyError:
        #         pass
        # print("found links: ", title_list)
        # influence_dict[physicist_id] = title_list

        # #simple code:
        # links_on_page = wikipedia.page(physicist_name).links
        # for link in links_on_page:
        #     page_id = find_wiki_page_id(link)
        #     if page_id in list_valid_ids:
        #         # print("link found:   ", page_id, link)
        #         title_list.append((page_id, link))
        # print("found links: ", title_list)
        # influence_dict[physicist_id] = title_list

        #complicated code:

        url = "https://en.wikipedia.org/w/api.php"
        session = requests.Session()
        params = {
            "action": "query",
            "format": "json",
            "titles": physicist_name,
            "prop": "links",
            "pllimit": "max"
        }

        response = session.get(url=url, params=params)
        data = response.json()
        pages = data["query"]["pages"]

        pg_count = 1


        for key, val in pages.items():
            for link in val["links"]:
                try:
                    title = link["title"]
                    page_id = name_to_id_dict[title]
                    if page_id in list_valid_ids:
                        title_list.append(title)
                except KeyError:
                    pass

        # while False:
        while "continue" in data:
            plcontinue = data["continue"]["plcontinue"]
            params["plcontinue"] = plcontinue
            response = session.get(url=url, params=params)
            data = response.json()
            pages = data["query"]["pages"]

            pg_count += 1

            # print("\nPage %d" % pg_count)
            for key, val in pages.items():
                for link in val["links"]:
                    try:
                        title = link["title"]
                        page_id = name_to_id_dict[title]
                        if page_id in list_valid_ids:
                            title_list.append(title)
                    except KeyError:
                        pass

        influence_dict[physicist_name] = title_list


    # Save the dictionary as a JSON string to the text file
    save_dict_txt(influence_dict, "social_network.txt")

    with open(output_txt, 'w', encoding='utf-8') as file:
        json.dump(influence_dict, file, ensure_ascii=False)


the_social_network("real_titles_ids.txt", "social_network.txt")
social_network = load_dict_json("social_network.txt")
print(social_network)


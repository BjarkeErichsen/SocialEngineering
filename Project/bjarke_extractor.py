import requests
from bs4 import BeautifulSoup
from wiki_extractor import find_wiki_page_id_from_url

def get_page_html(url):
    response = requests.get(url)
    return response.text

def extract_links(html, base_url='https://en.wikipedia.org'):
    soup = BeautifulSoup(html, 'html.parser')

    # Remove navboxes
    for navbox in soup.find_all('div', {'class': 'navbox'}):
        navbox.decompose()

    # Extract links
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/wiki/'):
            full_url = f'{base_url}{href}'
            print("page_id:", find_wiki_page_id_from_url(full_url))
            links.append(full_url)

    return links

def main():
    url = 'https://en.wikipedia.org/wiki/Albert_Einstein'
    html = get_page_html(url)
    links = extract_links(html)

    print(f'Found {len(links)} links:')
    for link in links:
        print(link)

if __name__ == '__main__':
    main()
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def extract_letter_links(letters_url: str, base_url: str) -> dict:
    """Extract the full URL of every Warren Buffet's annual letter to the
    shareholders of Berkshire Hathaway in a dictionary format

    Args:
        letters_url (str): Main landing page of Buffet's annual letters
        base_url (str): Base form of the URL where the letters are stored

    Returns:
        dict: Full links to each years annual letter, with the year as the key
              and the link as the value
    """

    # Download contents of annual Berkshire Hathaway shareholder letters page
    res = requests.get(letters_url,
                       headers={"User-Agent":
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    res.raise_for_status()

    # Parse downloaded page with BS4
    soup = BeautifulSoup(res.text, features='html.parser')

    # Create a dictionary of the full link of every shareholder letter
    # with the structure {year: full_url}
    links = {}
    for link in soup.find_all('a'):
        letter_url = link['href']
        if letter_url.endswith('html') or letter_url.endswith('pdf'):
            links[int(letter_url[:4])] = f'{base_url}/{letter_url}'

    return links


# TODO: Download the HTML and PDF files to the system
def download_letters(letter_links):
    pass


# TODO: Generate the wordcloud for each downloaded annual shareholder letter
def generate_worldcloud(letter_file):
    pass


if __name__ == '__main__':

    LETTERS_URL = "https://www.berkshirehathaway.com/letters/letters.html"
    BASE_URL = "https://www.berkshirehathaway.com/letters"

    letter_links = extract_letter_links(LETTERS_URL, BASE_URL)
    print('')

import os
from subprocess import run
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

    print('Extracting links to annual shareholder letters...')

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
            links[letter_url[:4]] = f'{base_url}/{letter_url}'

    # Loop through the first links and check for second-level PDF links
    for year, link in tqdm(links.items()):

        # Download and parse each HTML webpage
        res = requests.get(link,
                           headers={"User-Agent":
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        soup = BeautifulSoup(res.text, features='html.parser')

        # Check for pages with in-page PDF links (years 1998 to 2003)
        if 'Adobe Acrobat' in soup.text:
            # Find all secondary links
            in_page_links = soup.find_all('a')
            # Update the landing page link to the in-page PDF letter link
            for in_page_link in in_page_links:
                if 'pdf' in in_page_link["href"].lower():
                    pdf_link = f'{base_url}/{in_page_link["href"]}'
                    links[year] = pdf_link

    return links


def download_letters(links: dict, base_url: str) -> None:
    """Download all of Warren Buffet's annual letters to the shareholders as
    a TXT file

    Args:
        links (dict): Full links to each years annual letter, with the year
             as the key and the link as the value
    """

    print('Downloading shareholder letters...')

    # Loop through all links for each year
    for year, link in tqdm(links.items()):

        # Create the year folder if it does not exist
        folder_path = os.path.join(os.getcwd(), 'letters', year)
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

        # For HTML format letters
        if link.endswith('html'):

            # Download and parse the HTML webpage
            res = requests.get(link,
                               headers={"User-Agent":
                                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            soup = BeautifulSoup(res.text, features='html.parser')

            # Generate the TXT file path
            file_path = os.path.join(folder_path, f'{year}.txt')

            # Write the text of the HTML letter into a TXT file
            with open(file=file_path, mode='w', encoding='utf-8') as f:
                f.write(soup.text)

        # For PDF format letters
        else:

            # Download the contents of the PDF file
            res = requests.get(link, stream=True,
                               headers={"User-Agent":
                                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

            # Generate the file path of the PDF file
            file_path = os.path.join(folder_path, f'{year}.pdf')

            # Save the original PDF file
            with open(file=file_path, mode='wb') as f:
                f.write(res.content)

            # Extract the text of the PDF file to a TXT file
            run(f'pdf2txt.exe {file_path}')


if __name__ == '__main__':

    LETTERS_URL = "https://www.berkshirehathaway.com/letters/letters.html"
    BASE_URL = "https://www.berkshirehathaway.com/letters"

    letter_links = extract_letter_links(LETTERS_URL, BASE_URL)
    download_letters(letter_links, BASE_URL)

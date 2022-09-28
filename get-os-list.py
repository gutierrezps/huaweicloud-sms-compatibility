import json
import os

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'data')
FAQ_URL = 'https://support.huaweicloud.com/intl/en-us/sms_faq/sms_faq_0007.html'  # noqa
FAQ_HTML_FILE = os.path.join(OUTPUT_DIR, 'cache.html')
OS_LIST_JSON = os.path.join(OUTPUT_DIR, 'os-list.json')


def fetch_page_content() -> str:
    """If the FAQ_HTML_FILE doesn't exist, fetch the contents of FAQ_URL
    and save to it.

    Returns:
        str: HTML page content
    """
    page_content = ''

    if os.path.exists(FAQ_HTML_FILE):
        with open(FAQ_HTML_FILE, encoding='utf-8') as f:
            page_content = f.read()
    else:
        page_content = requests.get(FAQ_URL).text

        with open(FAQ_HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(page_content)

    return page_content


def extract_windows_details(table_tag: Tag) -> list:
    """Extracts the Windows compatibility details from the table HTML.

    Args:
        table_tag (Tag): Table 1 HTML code

    Returns:
        list: with each Windows entry
    """
    details = []
    remarks = ''

    for row in table_tag.tbody.find_all('tr'):
        data = [col.p.string for col in row.find_all('td')]

        os_name, bits, uefi = data[:3]

        # fourth column, when present, contain remarks
        if len(data) == 4:
            remarks = data[3]

        if remarks == 'N/A':
            remarks = ''

        details.append({
            'distro': 'Windows',
            'os_name': os_name,
            'bits': bits,
            'uefi_support': uefi.lower() == 'yes',
            'remarks': remarks
        })

    return details


def extract_linux_details(table_tag: Tag) -> list:
    """Extracts the Linux compatibility details from the table HTML.

    Args:
        table_tag (Tag): Table 2 HTML code

    Returns:
        list: with each Linux entry
    """
    details = []
    distro = ''
    remarks = ''

    for row in table_tag.tbody.find_all('tr'):
        data = [col.p.string for col in row.find_all('td')]
        if len(data) == 5:
            distro, os_name, bits, uefi, remarks = data
        elif len(data) == 4:
            os_name, bits, uefi, remarks = data
        else:
            os_name, bits, uefi = data

        if remarks == 'None':
            remarks = ''

        details.append({
            'distro': distro,
            'os_name': os_name,
            'bits': bits,
            'uefi_support': uefi.lower() == 'yes',
            'remarks': remarks
        })

    return details


def process_page_content(content: str) -> list:
    """Extract compatibility information from FAQ_URL HTML code.

    Examples of list items returned:

    {
        'distro': 'CentOS',
        'os_name': 'CentOS 6.1',
        'bits': 64,
        'uefi_support': 'no',
        'remarks': ''
    }

    Args:
        content (str): FAQ_URL HTML contents

    Returns:
        list: will all operating systems' details
    """
    soup = BeautifulSoup(content, 'html.parser')

    all_tables = soup.find_all('table')

    os_support = []

    win_details = extract_windows_details(all_tables[0])
    linux_details = extract_linux_details(all_tables[1])

    os_support.extend(win_details)
    os_support.extend(linux_details)

    return os_support


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    content = fetch_page_content()
    support_list = process_page_content(content)

    with open(OS_LIST_JSON, 'w', encoding='utf-8') as json_file:
        json.dump(support_list, json_file, indent=4)

from bs4 import BeautifulSoup
import requests
import urllib.parse
from collections import deque
import re

user_url = str(input('[+] Please Enter Target URL: '))
urls = deque([user_url])

scraping_urls = set()
emails = set()

count = 0
try:
    while urls:
        count += 1
        if count == 100:
            break
        url = urls.popleft()
        if url in scraping_urls:
            continue
        scraping_urls.add(url)

        parts = urllib.parse.urlsplit(url)
        base_url = '{0.scheme}://{0.netloc}'.format(parts)
        path = url[:url.rfind('/') + 1] if '/' in parts.path else url

        print('[%d] Processing %s' % (count, url))
        try:
            response = requests.get(url)
            response.raise_for_status()
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            print(f'Error fetching {url}: {e}')
            continue

        new_emails = set(re.findall(r'[a-z0-9\. \-+_]+@[a-z0-9\. \-+_]+\.[a-z]+', response.text, re.I))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, features="lxml")

        for anchor in soup.find_all("a"):
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
            if link.startswith('/'):
                link = urllib.parse.urljoin(base_url, link)
            elif not link.startswith('http'):
                link = urllib.parse.urljoin(path, link)
            
            if link not in scraping_urls and link not in urls:
                urls.append(link)

except KeyboardInterrupt:
    print('[-] Closing!')

for mail in emails:
    print(mail)


import requests
from firebase import firebase
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import time
from urllib.parse import urljoin, urlparse,urlunparse


import requests
from urllib.parse import urlparse, urljoin,quote, unquote
import re
import nltk







#works with hebrew title
def links_enrichment(links):
    meta = []
    for link in links:
        try:
            # Create a session object to manage redirections
            time.sleep(1)
            session = requests.Session()
            session.max_redirects = 10

            # Fetch the page content
            response = session.get(link, timeout=10)
            response.raise_for_status()

            # Ensure proper encoding (UTF-8) for Hebrew text
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract meta description
            meta_description = soup.find('meta', {'name': 'description'})
            description = meta_description['content'] if meta_description else "תיאור אינו זמין"

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.text if title_tag else "כותרת אינה זמינה"

            # Print the title for debugging
            print(f"Title: {title}")

            # Append metadata to the result
            meta.append({
                "link": link,
                "title": title.strip(),
                "description": description.strip()
            })
        except requests.Timeout:
            print(f"Timeout crawling {link}")
        except Exception as e:
            print(f"Error crawling {link}: {e}")
            meta.append({
                "link": link,
                "title": "כותרת אינה זמינה",
                "description": "תיאור אינו זמין"
            })
    return meta



# Function to delete a db table
def delete_node(node_path):
    delete_url = f"{url}/{node_path}.json"
    response = requests.delete(delete_url)
    if response.status_code == 200:
        print(f"Node '{node_path}' deleted successfully")
    else:
        print(f"Failed to delete node '{node_path}', Status code: {response.status_code}")






def decode_url(href):
    """Decode a URL that might be double-encoded."""
    try:
        # Decode the URL twice to handle double encoding
        decoded = unquote(unquote(href))
        return decoded
    except Exception as e:
        print(f"Error decoding URL: {href} - {e}")
        return href  # Return original if decoding fails


visited = set()

def crawl(url, max_depth, depth=0):
    if depth > max_depth:  # Stop if maximum depth is exceeded
        return

    if url in visited:  # Skip already visited URLs
        return

    visited.add(url)  # Mark the URL as visited
    print(f"Crawling: {url}")

    # Create a session object to manage redirections
    session = requests.Session()
    session.max_redirects = 10

    try:
        # Fetch the page content
        time.sleep(1)  # Respectful crawling: add a delay
        response = session.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Set the encoding explicitly for Hebrew support
        response.encoding = 'utf-8'

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract and process links
        for link in soup.find_all('a', href=True):
            href = link['href']


            # Decode the URL and re-encode it properly
            decoded_href = decode_url(href)
            encoded_href = quote(decoded_href, safe="/:&?=")  # Re-encode for proper URL usage

            # Resolve relative URLs into absolute URLs
            absolute_url = urljoin(url, encoded_href)

            # Validate domain to stay within the target site
            domain = urlparse(absolute_url).netloc
            if domain and (domain.endswith('.kizur.co.il') or domain == 'kizur.co.il'):
                if absolute_url not in visited:  # Avoid re-crawling
                    crawl(absolute_url, max_depth, depth + 1)

    except requests.Timeout:
        print(f"Timeout crawling {url}")
    except Exception as e:
        print(f"Error crawling {url}: {e}")

# Start crawling from the root URL
root_url = "http://www.kizur.co.il/home.php"
max_depth = 1
crawl(root_url, max_depth)
crawled_links =list(visited)
links = links_enrichment(crawled_links)


url = "https://query-kings-default-rtdb.europe-west1.firebasedatabase.app/"
FBconn = firebase.FirebaseApplication(url,None)

for link in links:
  FBconn.post('/pagesl/',link)







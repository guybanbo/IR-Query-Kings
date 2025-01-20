import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from collections import defaultdict, Counter
import re
from firebase import firebase
import math


def get_content(link):
    try:
        time.sleep(1)
        session = requests.Session()
        session.max_redirects = 10
        response = session.get(link, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.Timeout:
        print(f"Timeout crawling {link}")
    except Exception as e:
        print(f"Error crawling {link}: {e}")
    return ""

def extract_acronym_definitions(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr', valign='top')
    pairs = []
    for row in rows:
        columns = row.find_all('td', class_='sr_results')
        if len(columns) == 2:
            acronym = columns[0].get_text(strip=True)
            definition = columns[1].get_text(strip=True)
            pairs.append((acronym, definition))
    return pairs
#the average number of words in the definitions of abbreviations
#for categories of organizations and institutions
def query1(links):
    total_words = 0
    total_definitions = 0

    all_data = []
    document_word_index = defaultdict(list)  # Dictionary to track words per document
    all_words = []  # List to track all words for frequency analysis

    for doc_id, data in links.items():
        link = data["link"]
        print(f"Processing: {link}")
        html_content = get_content(link)
        if not html_content:
            continue
        pairs = extract_acronym_definitions(html_content)

        # Extract the page number from the link
        page_match = re.search(r"page=(\d+)", link)
        page_number = page_match.group(1) if page_match else "unknown"

        for acronym, definition in pairs:
            all_data.append({
                "Link": link,
                "Acronym": acronym,
                "Definition": definition
            })
            total_words += len(definition.split())
            total_definitions += 1

            # Add words from the definition to the index for this page
            words = definition.split()
            document_word_index[page_number].extend(words)
            all_words.extend(words)  # Collect all words for frequency analysis

    # Calculate average words per definition
    avg_words = total_words / total_definitions if total_definitions > 0 else 0

    # Add average as a separate row
    all_data.append({
        "Link": "Average Across All Definitions",
        "Acronym": "",
        "Definition": f"Average Words: {avg_words:.2f}"
    })

    # Prepare document index data
    index_data = []
    for page_number, words in document_word_index.items():
        index_data.append({
            "Document": f"{page_number}",
            "Index": ",".join(sorted(set(words)))
        })

    # Get the 15 most common words
    word_counts = Counter(all_words)
    most_common_words = word_counts.most_common(15)
    common_words_data = [
        {"Word": word, "Count": count} for word, count in most_common_words
    ]

    # Build inverted index for the 15 most common words
    inverted_index_data = []
    for word, _ in most_common_words:
        pages_containing_word = [
            f"{page_number}" for page_number, words in document_word_index.items() if word in words
        ][:20]  # Limit to a maximum of 20 pages
        inverted_index_data.append({
            "Word": word,
            "Documents": ",".join(pages_containing_word)
        })

    # Calculate TF-IDF
    total_documents = len(document_word_index)
    tfidf_data = []
    for word, _ in most_common_words:
        idf = (
            math.log(total_documents / sum(1 for words in document_word_index.values() if word in words))
        )
        for page_number, words in document_word_index.items():
            tf = words.count(word)
            tfidf = tf * idf
            tfidf_data.append({
                "Word": word,
                "Page": int(page_number),
                "TF": tf,
                "IDF": idf,
                "TF-IDF": tfidf
            })

    # Convert to DataFrames
    df_acronyms = pd.DataFrame(all_data)
    df_index = pd.DataFrame(index_data)
    df_common_words = pd.DataFrame(common_words_data)
    df_inverted_index = pd.DataFrame(inverted_index_data)
    df_tfidf = pd.DataFrame(tfidf_data)
    # Group by "Word" and sort by "Page" within each group
    from itertools import groupby

# Sort the data first by "Word" then by "Page"
    tfidf_data.sort(key=lambda x: (x['Word'], x['Page']))
# Convert to DataFrame
    df_tfidf = pd.DataFrame(tfidf_data)


    # Export to Excel with styling
    filename = 'Query1.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_acronyms.to_excel(writer, index=False, sheet_name='Acronyms')
        df_index.to_excel(writer, index=False, sheet_name='Index')
        df_common_words.to_excel(writer, index=False, sheet_name='Common Words')
        df_inverted_index.to_excel(writer, index=False, sheet_name='Inverted Index')
        df_tfidf.to_excel(writer, index=False, sheet_name='TF-IDF')
        workbook = writer.book

        # Style Acronyms sheet
        worksheet_acronyms = writer.sheets['Acronyms']
        header_font = Font(bold=True)
        for col in worksheet_acronyms.iter_cols(min_row=1, max_row=1):
            for cell in col:
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')

        for col in worksheet_acronyms.columns:
            max_length = 0
            col_letter = col[0].column_letter  # Get the column letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            adjusted_width = max_length + 2
            worksheet_acronyms.column_dimensions[col_letter].width = adjusted_width


    print(f"Data exported to {filename} successfully.")

# Firebase connection and data fetching
url = "https://query-kings-default-rtdb.europe-west1.firebasedatabase.app/"
FBconn = firebase.FirebaseApplication(url, None)
result = FBconn.get('/pages', None)
filtered_records = {
    doc_id: data for doc_id, data in result.items()
    if data["link"].startswith('http://www.kizur.co.il/search_group.php?group=10')
}
query1(filtered_records)

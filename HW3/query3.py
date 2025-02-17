import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from collections import defaultdict, Counter
import re

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

def extract_acronym_definitions_with_categories(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr', valign='top')
    pairs = set()  # Use set to ensure unique pairs

    for row in rows:
        columns = row.find_all('td', class_='sr_results')
        if len(columns) >= 3:  # Ensure there are at least three columns
            acronym = columns[0].get_text(strip=True).lower()
            definition = columns[1].get_text(strip=True).lower()

            # Extract categories
            category_links = columns[2].find_all('a', class_='group_word_link') if columns[2] else []
            categories = ", ".join(link.get_text(strip=True) for link in category_links)
            if not categories:
              categories = "אחר"  # Default to "אחר" if no categories found


            pairs.add((acronym, definition, categories))
    return list(pairs)


def query3(links):
    acronym_def_count = defaultdict(int)
    all_data = []
    document_word_index = defaultdict(set)
    all_words = []
    seen_pairs = set()

    for idx, data in enumerate(links, start=1):
        page_number = str(idx)
        link = data["link"]
        print(f"Processing: {link}")
        html_content = get_content(link)
        if not html_content:
            continue
        pairs = extract_acronym_definitions_with_categories(html_content)

        for acronym, definition, categories in pairs:
            if (acronym, definition, categories) not in seen_pairs:
                seen_pairs.add((acronym, definition, categories))
                all_data.append({
                    "Link": link,
                    "Acronym": acronym,
                    "Definition": definition,
                    "Category": categories,
                    "Page": page_number,
                })
                acronym_def_count[acronym] += 1
                words = definition.split()
                document_word_index[page_number].update(words)
                all_words.extend(words)

    # Calculate statistics
    total_acronyms = len(acronym_def_count)
    total_definitions = sum(acronym_def_count.values())
    avg_definitions_per_acronym = total_definitions / total_acronyms if total_acronyms > 0 else 0

    all_data.append({
        "Link": "Average Across All Acronyms",
        "Acronym": "",
        "Definition": f"Average Definitions: {avg_definitions_per_acronym:.2f}",
        "Category": "",
        "Page": "",
    })

    # Prepare document index and common word data
    index_data = []
    for page_number, words in document_word_index.items():
        index_data.append({
            "Document": f"{page_number}",
            "Index": ",".join(sorted(words)),
        })

    word_counts = Counter(all_words)
    most_common_words = word_counts.most_common(15)
    common_words_data = [{"Word": word, "Count": count} for word, count in most_common_words]

    inverted_index_data = []
    for word, _ in most_common_words:
        pages_containing_word = [
            f"{page_number}" for page_number, words in document_word_index.items() if word in words
        ][:20]
        inverted_index_data.append({
            "Word": word,
            "Documents": ",".join(pages_containing_word),
        })

    # Convert to DataFrames
    df_acronyms = pd.DataFrame(all_data)
    df_index = pd.DataFrame(index_data)
    df_common_words = pd.DataFrame(common_words_data)
    df_inverted_index = pd.DataFrame(inverted_index_data)

    # Export to Excel
    filename = 'Query 3.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_acronyms.to_excel(writer, index=False, sheet_name='Acronyms')
        df_index.to_excel(writer, index=False, sheet_name='Index')
        df_common_words.to_excel(writer, index=False, sheet_name='Common Words')
        df_inverted_index.to_excel(writer, index=False, sheet_name='Inverted Index')

        workbook = writer.book
        header_font = Font(bold=True)

        for sheet_name in ['Acronyms', 'Index', 'Common Words', 'Inverted Index']:
            worksheet = writer.sheets[sheet_name]
            for col in worksheet.iter_cols(min_row=1, max_row=1):
                for cell in col:
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')

            for col in worksheet.columns:
                max_length = 0
                col_letter = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass
                adjusted_width = max_length + 2
                worksheet.column_dimensions[col_letter].width = adjusted_width

    print(f"Data exported to {filename} successfully.")

from firebase import firebase
url = "https://query-kings-default-rtdb.europe-west1.firebasedatabase.app/"
FBconn = firebase.FirebaseApplication(url, None)
result = FBconn.get('/pages', None)
# Run the updated query function
filtered_records = [
    data for doc_id, data in result.items()
    if data["link"].startswith('http://www.kizur.co.il/search_word')
]

query3(filtered_records)
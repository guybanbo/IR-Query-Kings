# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 19:59:19 2025

@author: USER
"""

def calculate_new_pagerank(current_ranks, links, damping_factor=0.85):
    num_pages = len(current_ranks)
    new_ranks = {page: (1 - damping_factor) / num_pages for page in current_ranks}

    # Calculate contributions from incoming links
    for page in current_ranks:
        for target in links.get(page, []):  # Outgoing links from page
            num_outgoing = len(links[page])
            if num_outgoing > 0:
                new_ranks[target] += damping_factor * (current_ranks[page] / num_outgoing)

    return new_ranks


def print_ranks(ranks, iteration):
    print(f"\nPageRank values after iteration {iteration}:")
    print("-" * 35)
    print("Page  |  PageRank Value")
    print("-" * 35)
    for page, rank in sorted(ranks.items()):
        print(f"  {page}   |     {rank:.5f}")
    print("-" * 35)

urls=["http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%92%D7%97&m=3", "http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%92%D7%97%D7%A9&m=3","http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%92%D7%A9&m=3"
,"http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%92%D7%99&m=3","http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%91%D7%90&m=3", "http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%93&m=3"
"http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%91%D7%92&m=3","http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%90&m=3","http://www.kizur.co.il/search_word.php?abbr=%D7%90&m=3"
,"http://www.kizur.co.il/search_word.php?abbr=%D7%90%D7%90%D7%91&m=3"]


# Assign letters to URLs
url_to_letter = {url: chr(65 + i) for i, url in enumerate(urls)}

# Web structure (links between pages)
links = {
    'A': ['B', 'D'],
    'B': ['D'],
    'C': ['F', 'G'],
    'D': ['E'],
    'E': ['G'],
    'F': ['G'],
    'G': ['H', 'I'],
    'H': ['I'],
    'I': ['H', 'J'],
    'J': ['H', 'I'],
}

# Initialize PageRank values (1/number_of_pages for each page)
pages = list(links.keys())
num_pages = len(pages)
current_ranks = {page: 1 / num_pages for page in pages}

# Print initial values
print("\nInitial PageRank Values:")
print_ranks(current_ranks, 0)

# Perform iterations
iterations = 5
for i in range(1, iterations + 1):
    current_ranks = calculate_new_pagerank(current_ranks, links)
    print_ranks(current_ranks, i)

# Find highest PageRank after all iterations
highest_page = max(current_ranks.items(), key=lambda x: x[1])
print(f"\nHighest PageRank after {iterations} iterations:")
print(f"Page {highest_page[0]} with PageRank value of {highest_page[1]:.5f}")

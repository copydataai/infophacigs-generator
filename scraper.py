import requests
from bs4 import BeautifulSoup
import json
import urllib.parse

def google_search(query, num_results=10):
    # Encode the query for URL
    encoded_query = urllib.parse.quote(query)

    # Construct the Google search URL
    url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"

    # Send a GET request to Google
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    print(response.ok, response.url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    keywords = query.split()
    print(keywords)

    # Extract search result links
    search_results = []

    # TODO: improve the search by attrs to check by children h3 and keywords
    links = soup.find_all('a', { "jsname": "UWckNb"})
    for result in links:

        link = result['href']
        title = result.select_one('h3').text if result.select_one('h3') else "No title"
        search_results.append({"title": title, "link": link})

    return search_results

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    search_query = input("Enter your search query: ")
    num_results = int(input("Enter the number of results to fetch (default is 10): ") or 10)

    results = google_search(search_query, num_results)

    # Save results to JSON file
    save_to_json(results, "search_results.json")

    print(f"Search results have been saved to search_results.json")

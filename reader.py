import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import random
import time
import re

def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(user_agents)


def fetch_content(url):
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)

        if "login" in response.url.lower() or "captcha" in response.url.lower():
            return "Content protected. Unable to fetch."

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find the main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main', re.I))

        if main_content:
            paragraphs = main_content.find_all('p')
        else:
            paragraphs = soup.find_all('p')

        content = ' '.join([p.text for p in paragraphs if len(p.text.split()) > 5])  # Only include paragraphs with more than 5 words
        content = re.sub(r'\s+', ' ', content).strip()
        return content[:1000]  # Return first 1000 characters
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch content. Error: {str(e)}"


def create_blog_post(search_results):
    blog_post = "# Blog Post Based on Search Results\n\n"

    for result in search_results:
        blog_post += f"## {result['title']}\n\n"
        blog_post += f"Source: {result['link']}\n\n"
        content = fetch_content(result['link'])
        blog_post += f"{content}...\n\n"
        blog_post += "---\n\n"
        time.sleep(random.uniform(1, 3))  # Random delay between requests

    return blog_post

def save_blog_post(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    search_results = read_json("search_results.json")
    blog_post = create_blog_post(search_results)
    save_blog_post(blog_post, "blog_post.md")
    print("Blog post has been generated and saved as blog_post.md")

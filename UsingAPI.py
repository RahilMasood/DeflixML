import requests

def get_nytimes_movie_review_url(movie_name, api_key):
    # Define the API URL and the query parameters
    base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    query = f"section_name:\"Movies\" AND type_of_material:\"Review\" AND {movie_name}"
    
    # Make the GET request to the API
    params = {
        "q": query,
        "api-key": api_key
    }
    
    try:
        # Send the GET request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception if the response code is 4xx/5xx
        
        # Parse the response JSON
        data = response.json()
        
        # Check if there are any articles in the response
        if "response" in data and "docs" in data["response"]:
            articles = data["response"]["docs"]
            if articles:
                # Get the first article that matches the search
                first_article = articles[0]
                article_url = first_article.get("web_url")
                title = first_article.get("headline", {}).get("main", "No title available")
                return article_url, title
            else:
                return None, "No review found"
        else:
            return None, "No review found"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from NYTimes API: {e}")
        return None, "Error fetching data"

def get_review_content(url):
    try:
        # Fetch the review content from the article URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Extract the content (for simplicity, we're returning the entire article as text)
        # You might want to use a library like BeautifulSoup to extract just the review content.
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the article content: {e}")
        return "Error fetching the article content"

def main():
    movie_name = input("Enter the movie name: ")
    api_key = input("Enter your NYTimes API key: ")

    # Get the review URL from the API
    url, title = get_nytimes_movie_review_url(movie_name, api_key)
    
    if url:
        print(f"\nFound review URL: {url}\n")
        print(f"Title: {title}")
        
        # Fetch and print the content of the review article
        review_content = get_review_content(url)
        print("\nContent:")
        print(review_content)
    else:
        print("No review URL found")

if __name__ == "__main__":
    main()

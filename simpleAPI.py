import requests

# Function to fetch movie reviews by movie name
def get_movie_reviews(movie_name, api_key):
    # URL for the Article Search API with filters for movie reviews
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    
    # Query parameters
    params = {
        'q': movie_name,  # The movie name to search for
        'fq': 'section_name:"Movies" AND type_of_material:"Review"',  # Filter to get movie reviews
        'api-key': api_key  # Your New York Times API key
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Check if we have any articles in the response
        if 'response' in data and 'docs' in data['response']:
            articles = data['response']['docs']
            if articles:
                # Loop through and display the results
                print(f"Found {len(articles)} review(s) for '{movie_name}':\n")
                for article in articles:
                    title = article.get('headline', {}).get('main', 'No Title')
                    url = article.get('web_url', 'No URL')
                    snippet = article.get('snippet', 'No Snippet')
                    print(f"Title: {title}")
                    print(f"URL: {url}")
                    print(f"Snippet: {snippet}\n")
            else:
                print(f"No reviews found for '{movie_name}' in the New York Times.")
        else:
            print(f"No articles found in the response.")
    else:
        print(f"Error: Unable to fetch data. Status Code: {response.status_code}")

# Main function to enter movie name and get reviews
def main():
    # Enter your API key here
    api_key = 'yourkey'  # Replace 'yourkey' with your actual NY Times API key
    
    # Ask user for movie name
    movie_name = input("Enter the name of the movie to search for reviews: ")
    
    # Call the function to get movie reviews
    get_movie_reviews(movie_name, api_key)

if __name__ == "__main__":
    main()

import tweepy

# Function to authenticate and set up API client
def authenticate_twitter(api_key, api_secret_key, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

# Function to fetch the first 30 tweets related to a given movie
def get_movie_reviews(movie_name, api):
    # Query to search for tweets mentioning the movie
    query = f"{movie_name} -filter:retweets"  # Excluding retweets
    tweets = api.search_tweets(q=query, count=30, lang="en", tweet_mode='extended')
    
    # Collect and print the tweet details
    reviews = []
    for tweet in tweets:
        reviews.append({
            'user': tweet.user.screen_name,
            'tweet': tweet.full_text
        })
    
    return reviews

# Main function
def main():
    # Get user input for the movie name
    movie_name = input("Enter the name of the new movie: ")
    
    # Enter your Twitter API credentials here
    api_key = "your-api-key"
    api_secret_key = "your-api-secret-key"
    access_token = "your-access-token"
    access_token_secret = "your-access-token-secret"
    
    # Authenticate and get the API client
    api = authenticate_twitter(api_key, api_secret_key, access_token, access_token_secret)
    
    # Fetch and display the first 30 tweets about the movie
    reviews = get_movie_reviews(movie_name, api)
    
    if reviews:
        print(f"\nFirst 30 tweets about '{movie_name}':\n")
        for i, review in enumerate(reviews, 1):
            print(f"{i}. @{review['user']} said: {review['tweet']}\n")
    else:
        print(f"No tweets found for {movie_name}.")

if __name__ == "__main__":
    main()

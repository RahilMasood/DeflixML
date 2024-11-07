#https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
#Install dataset here

import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error
import joblib


# Load the IMDb dataset (or your custom dataset)
movie_df = pd.read_csv("path_to_your_imdb_dataset.csv")
movie_df.head()  # Check the dataset structure

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

movie_df['cleaned_review'] = movie_df['review'].apply(preprocess_text)


# Create the vectorizer and transform the review text into a matrix of features
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(movie_df['cleaned_review'])

# Target variable: movie ratings
y = movie_df['rating']  # Assuming the ratings are in a column named 'rating'

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# Predict the ratings on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")


# Save the trained model and vectorizer to disk
joblib.dump(model, 'movie_rating_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

def generate_rating(review_text):
    # Preprocess the review text (same as during training)
    cleaned_review = preprocess_text(review_text)
    
    # Load the trained model and vectorizer
    model = joblib.load('movie_rating_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    
    # Vectorize the cleaned review text
    review_vector = vectorizer.transform([cleaned_review])
    
    # Predict the movie rating
    rating = model.predict(review_vector)[0]
    
    # Ensure rating is between 0 and 10
    rating = max(0, min(10, round(rating, 1)))
    
    return rating

def main():
    movie_name = input("Enter the movie name: ")
    url = get_nytimes_movie_review_url(movie_name)
    
    if url:
        print(f"\nFound review URL: {url}\n")
        result = get_review_content(url)
        rating = generate_rating(result['content'])
        print(f"Rating for the movie: {rating}/10")
    else:
        print("No review URL found")

if __name__ == "__main__":
    main()

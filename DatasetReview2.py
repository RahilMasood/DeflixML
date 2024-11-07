import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import joblib
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import DataLoader
import torch
from datasets import Dataset


# Load the IMDb dataset
# Replace with the actual path to your dataset
movie_df = pd.read_csv("path_to_imdb_dataset.csv")

# Example of dataset format
# movie_df.head()

# Preprocessing function (removes stopwords and punctuation)
def preprocess_text(text):
    # Remove non-alphanumeric characters and convert to lower case
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    # Tokenization
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

# Preprocess the reviews
movie_df['cleaned_review'] = movie_df['review'].apply(preprocess_text)

# Splitting the dataset into training and testing sets
X = movie_df['cleaned_review']
y = movie_df['sentiment']  # assuming 'sentiment' column is 0 for negative and 1 for positive
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorize the text using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train a Naive Bayes classifier
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test_vec)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy*100:.2f}%")

# Save the model and vectorizer
joblib.dump(model, 'sentiment_classifier_model.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')

# Function to generate the rating using the trained model
def generate_rating_from_model(review_text):
    # Preprocess the review text (same as during training)
    cleaned_review = preprocess_text(review_text)
    
    # Load the trained model and vectorizer
    model = joblib.load('sentiment_classifier_model.pkl')
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    
    # Vectorize the cleaned review text
    review_vector = vectorizer.transform([cleaned_review])
    
    # Predict the sentiment
    sentiment = model.predict(review_vector)[0]
    
    # Assign a rating based on sentiment (positive -> 10, negative -> 0)
    if sentiment == 1:  # Positive
        rating = 10
    else:  # Negative
        rating = 0
    
    return rating

# Main function to integrate with your existing review scraping logic
def main():
    movie_name = input("Enter the movie name: ")
    url = get_nytimes_movie_review_url(movie_name)
    
    if url:
        print(f"\nFound review URL: {url}\n")
        result = get_review_content(url)
        detailed_review = result['content']  # Extracted detailed review content
        
        # Get the sentiment-based rating for the detailed review
        rating = generate_rating_from_model(detailed_review)
        print(f"Rating for the movie: {rating}/10")
    else:
        print("No review URL found")

if __name__ == "__main__":
    main()

# Tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Tokenize the data (you would need to tokenize your dataset for training)
def tokenize_function(examples):
    return tokenizer(examples['review'], padding='max_length', truncation=True)

# Example of preparing your dataset for training using Hugging Face's Datasets library
train_data = Dataset.from_pandas(movie_df[['review', 'sentiment']])

# Tokenize the data
train_data = train_data.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir='./results',          
    num_train_epochs=3,              
    per_device_train_batch_size=8,  
    per_device_eval_batch_size=8,   
    warmup_steps=500,               
    weight_decay=0.01,              
    logging_dir='./logs',            
)

# Trainer
trainer = Trainer(
    model=model,                         
    args=training_args,                  
    train_dataset=train_data,         
)

# Train the model
trainer.train()

# Save the model
model.save_pretrained('sentiment_model_bert')
tokenizer.save_pretrained('sentiment_model_bert')


# Load the model and tokenizer
model = BertForSequenceClassification.from_pretrained('sentiment_model_bert')
tokenizer = BertTokenizer.from_pretrained('sentiment_model_bert')

def generate_rating_from_bert(review_text):
    inputs = tokenizer(review_text, return_tensors='pt', truncation=True, padding=True)
    outputs = model(**inputs)
    logits = outputs.logits
    sentiment = torch.argmax(logits).item()
    
    # Assign rating based on sentiment
    rating = 10 if sentiment == 1 else 0
    return rating

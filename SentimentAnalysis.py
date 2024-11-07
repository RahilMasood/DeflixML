import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
import os
import pandas as pd
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split 
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification


nltk.download("punkt")
nltk.download("stopwords")

text = "This is an example sentance to demo tokenization in NLP"

tokens = word_tokenize(text)
print(tokens)
stopwords = set(stopwords.words("english"))
print(stopwords)
#filtered_words = [word for word in words if word not in stopwords]
filtered_words =[]
for t in tokens:
    if t not in stopwords:
        filtered_words.append(t)
print(filtered_words)
stemmer = PorterStemmer()
stemmed_words = [stemmer.stem(t) for t in filtered_words]
print(stemmed_words)
vectorizer = Tf idf Vectorizer()
X = vectorizer.fit_transform(stemmed_words)
print(X.toarray())
warnings.filterwarnings("ignore")

for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
movie_df = pd.read_csv("/kaggle/input/imdb-dataset-of-50k-movie-reviews/IMDB Dataset.csv")
movie_df.head()
movie_df_subset = movie_df[:200]
movie_df_subset.shape


def preprocess(text):
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]

    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in filtered_words]
    return ''.join(stemmed_words)
        
movie_df_subset['review'] = movie_df_subset['review'].apply(preprocess) 
print(movie_df_subset['review'])
X = movie_df_subset['review']
y = movie_df_subset['sentiment']

vectorize = TfidfVectorizer()
X = vectorize.fit_transform(X)

X_train,X_test,y_train,y_test = train_test_split(X,y, test_size=0.2,random_state=42)

nlp_model = MultinomialNB()

nlp_model.fit(X_train,y_train)
y_pred = nlp_model.predict(X_test)

accuracy = accuracy_score(y_test,y_pred)
accuracy


tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

sentence = "This is a good example sentance to demo huggingface pretrained model in NLP"

tokens = tokenizer(sentence, return_tensors="pt")

with torch.no_grad():
    output_model = model(**tokens)
    
sentiment =  output_model.logits.argmax().item()
print(sentiment)

sentiment_map ={0:"negative", 1:"positive"}
print(sentiment_map[sentiment])

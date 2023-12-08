import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess(text):
    # Tokenisation
    words = word_tokenize(text)

    # Suppression des stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.lower() not in stop_words]

    # Lemmatisation
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # # stemming
    # stemmer = PorterStemmer()
    # words = [stemmer.stem(word) for word in words]

    # Reconstitution du texte après prétraitement
    processed_text = ' '.join(words)
    return processed_text
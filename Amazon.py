
#import libraries
import re
import nltk  
import string 
import itertools
import pandas as pd
from pickle import dump,load

from nltk import tokenize
from nltk.corpus import stopwords
from unicodedata import normalize
from textblob import TextBlob, Word

from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import  TfidfVectorizer
nltk.download("stopwords")

import streamlit as st 
########################### 


import base64
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-position: 55% 75%;
        background-size: contain;
        background-repeat: no-repeat
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local("amazon.png") 

st.title("**Sentiment Analysis of Amazon Reviews**")

def review_cleaning(text): 
    stop_words = stopwords.words('english')
    stop_words.extend(["sxsw","@","rt","re","w","u","m","s","sxswi","mention","link","amp","sx","sw","wi","sxs","google","app",
                       "phone","pad","apple","austin","quot","android","ipad","marissa","mayer","social","network","store",
                       "via","popup","called","zlf","zms","quotmajorquot"]) 
    
    text = normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore") # Encoding & Decoding Data
    text = re.sub("\[.*?\]","", text)                                                  #brackets
    text = re.sub("https?://\S+|www\.\S+", "", text)                                   #links
    text = re.sub("<.*?>+", "", text)                                                  #characters
    text = re.sub("[%s]" % re.escape(string.punctuation), "", text)                    #punctuations
    text = re.sub("\n","", text)                                                       #new line
    text = re.sub("\w*\d\w*","", text)                                                 #numbers
    text = " ".join([s for s in re.split("([A-Z][a-z]+[^A-Z]*)",text) if s])           #Split attached Uppercase words
    text = "".join("".join(s)[:2] for _, s in itertools.groupby(text))                 #remove letter repeating twice in continuation
    text = str(text).lower()                                                           #Normalization
    text = " ".join(s for s in str(text).split() if s not in stop_words)               #stopwords
    text = " ". join([w.lemmatize() for w in TextBlob(text).words])                    #Lemmatizaion
    return text

def Polarity(review):    
    return TextBlob(review).sentiment.polarity

def vec(text):
    tf = TfidfVectorizer().fit_transform(text).toarray()
    return pd.DataFrame(tf)


input_review = st.text_input("**:green[Review]**", "Type Here")
product_type = st.selectbox("**:green[Product Type]**",("0","1","2","3","4","5","6","7","8","9"))

az = pd.read_csv("Product_details.csv") 
amazon = pd.DataFrame(az["Product_Description"])
amazon.loc[len(amazon)] = [input_review]
amazon["Product_Description"] = amazon["Product_Description"].values.astype(str)
amazon["Product_Description"] = amazon["Product_Description"].apply(review_cleaning)
result = amazon["Product_Description"].iloc[-1:].to_string(index = False)
tfi = vec(amazon["Product_Description"])
#tfi.columns = tfi.columns.astype(str)
tf = tfi.iloc[-1:]
polar = Polarity(result)
tf["Product_Type"] = product_type
tf["Polarity_score"] = polar

st.markdown("**:green[User Input parameters]**")
inp = pd.DataFrame({"Review":result, "Product Type":product_type, "Polarity Score":round(polar,4)},index = [0])
st.write(inp)

def user_input_features_text():
    tf.columns = tf.columns.astype(str)
    return tf 

df = user_input_features_text()


loaded_model = load(open("Amazon.sav", "rb"))


if st.button("**Predict**"):
    prediction = loaded_model.predict(df)
    st.subheader("Sentiment")
    st.subheader(prediction[0])

if st.button("**Download ???**"):
    prediction = loaded_model.predict(df)
    output=pd.concat([df,pd.DataFrame(prediction)],axis=1)
    output.to_csv("prediction.csv")






































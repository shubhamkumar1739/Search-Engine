#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from pymongo import MongoClient
import math
import numpy as np
import utilities

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

suffixes = {
    1: ["ो", "े", "ू", "ु", "ी", "ि", "ा"],
    2: ["कर", "ाओ", "िए", "ाई", "ाए", "ने", "नी", "ना", "ते", "ीं", "ती", "ता", "ाँ", "ां", "ों", "ें"],
    3: ["ाकर", "ाइए", "ाईं", "ाया", "ेगी", "ेगा", "ोगी", "ोगे", "ाने", "ाना", "ाते", "ाती", "ाता", "तीं", "ाओं", "ाएं", "ुओं", "ुएं", "ुआं"],
    4: ["ाएगी", "ाएगा", "ाओगी", "ाओगे", "एंगी", "ेंगी", "एंगे", "ेंगे", "ूंगी", "ूंगा", "ातीं", "नाओं", "नाएं", "ताओं", "ताएं", "ियाँ", "ियों", "ियां"],
    5: ["ाएंगी", "ाएंगे", "ाऊंगी", "ाऊंगा", "ाइयाँ", "ाइयों", "ाइयां"],
}

def hi_stem(word):
    for L in 5, 4, 3, 2, 1:
        if len(word) > L + 1:
            for suf in suffixes[L]:
                if word.endswith(suf):
                    return word[:-L]
    return word

def get_text(filename) :
    file = open(filename, "r")
    text = file.read()
    file.close()
    return text

def remove_stopwords(text) :
    
    stopwords_set = ["|", "/", "\\", "." ,",", ")", "(", "-", "!", "~", "@"]
    for stopword in stopwords_set :
        text = text.replace(stopword, " ")
    
    return text

def stem_file(text) :
    text = sent_tokenize(text)
    tokens = set()
    ps = PorterStemmer()

    word_frequency = {}
    stem_frequency = {}
    num_words = 0
    
    for line in text :
        words = word_tokenize(line)
        num_words += len(words)
        stemmed_words = [hi_stem(word) for word in words]
        stemmed_words = [ps.stem(word) for word in stemmed_words]
        for i in range(len(words)) :
            tokens.add((words[i], stemmed_words[i], i))

            if words[i] not in word_frequency :
                word_frequency[words[i]] = 1
            else :
                word_frequency[words[i]] += 1
            if stemmed_words[i] not in stem_frequency :
                stem_frequency[stemmed_words[i]] = 1
            else :
                stem_frequency[stemmed_words[i]] += 1


    for word in word_frequency :
        word_frequency[word] /= num_words
    for stem in stem_frequency :
        stem_frequency[stem] /= num_words
    
    '''
        tokens -> (original_word, stemmed_word, line_number)
    '''
    return tokens, word_frequency, stem_frequency


# In[2]:


client = MongoClient()
db = client["search_engine"]


# In[3]:


# In[4]:


def get_matching_docs(words, stems) :
    stem_df = pd.DataFrame(db.stem_frequency_logs.find({"stem" : {"$in" : stems}}, {"_id" : 0}))
    df_counts = pd.DataFrame(stem_df.value_counts("stem"))
    df_counts["stem"] = df_counts.index
    df_counts.reset_index(drop = True, inplace = True)
    no_docs = pd.DataFrame(db.updated_logs.find({},{"filename" : 1})).count()[0]
    df_counts.columns = ["no_data","stem"]
    df_counts["idf"] = df_counts["no_data"].apply(lambda x : math.log(no_docs / x))
    
    merged_df = df_counts.merge(stem_df, left_on = "stem", right_on = "stem")
    merged_df["tf_idf"] = merged_df["term_frequency"] * merged_df["idf"]
    merged_df.drop(["idf", "term_frequency", "no_data"], axis = 1, inplace = True)
    
    word_df = pd.DataFrame(db.word_frequency_logs.find({"word" : {"$in" : words}}, {"_id" : 0}))
    df_counts = pd.DataFrame(word_df.value_counts("word"))
    df_counts["word"] = df_counts.index
    df_counts.reset_index(drop = True, inplace = True)
    df_counts.columns = ["no_data", "word"]
    df_counts["idf"] = df_counts["no_data"].apply(lambda x : math.log(no_docs / x))
                           
    merged_df_2 = df_counts.merge(word_df, left_on = "word", right_on = "word")
    merged_df_2["tf_idf"] = merged_df_2["term_frequency"] * merged_df_2["idf"]
    merged_df_2.drop(["idf", "term_frequency", "no_data"], axis = 1, inplace = True)
    return merged_df, merged_df_2


# In[11]:


def get_scores(words, stems) :
    df, df2 = get_matching_docs(words, stems)
    df = pd.DataFrame(df.groupby("filename").tf_idf.agg(sum))
    df.reset_index(inplace = True)
    df2 = pd.DataFrame(df2.groupby("filename").tf_idf.agg(sum))
    df2.reset_index(inplace = True)
    merged_df = df.merge(df2, how = "outer", on = "filename")
    merged_df.replace(np.nan, 0, inplace = True)
    merged_df["tf_idf"] = merged_df["tf_idf_x"] + merged_df["tf_idf_y"]
    merged_df.drop(["tf_idf_x", "tf_idf_y"], axis = 1, inplace = True)
    return merged_df


# In[18]:


def run(text) :
    tokens, a, b = stem_file(text)
    words = [token[0] for token in tokens]
    stems = [token[1] for token in tokens]
    scores = get_scores(words, stems)
    scores.sort_values("tf_idf", ascending = False, inplace = True)
    return list(scores["filename"])


# In[19]:


text = "विख्यात हैमिग्व आत्म"
files = run(text)
files


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
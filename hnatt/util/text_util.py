# from nltk import tokenize
# from nltk.corpus import stopwords
#
# STOP_WORDS = set(stopwords.words('english'))
#
#
# def normalize2(text):
# 	# text = text.decode('utf-8', 'ignore')
# 	text = text.lower().strip()
# 	sentences = tokenize.sent_tokenize(text)
# 	filtered_sentences = []
# 	for sentence in sentences:
# 		filtered_tokens = list()
# 		sentence = sentence.split()
# 		for w in sentence:
# 			w = w.strip()
# 			if len(w) > 0 and w not in STOP_WORDS:
# 				filtered_tokens.append(w)
# 		filtered_sentences.append(' '.join(filtered_tokens))
# 	return filtered_sentences

import re


def normalize(text):
    text = text.decode('utf-8', 'ignore')
    text = text.lower().strip()
    sentences = text.split('.')
    filtered_sentences = []
    for sentence in sentences:
        sentence = re.sub(' +', ' ', sentence.strip())
        if sentence:
            filtered_sentences.append(sentence)
    return filtered_sentences

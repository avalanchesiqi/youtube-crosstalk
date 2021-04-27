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

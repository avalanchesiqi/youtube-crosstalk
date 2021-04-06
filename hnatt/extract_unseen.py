import string, re
import pandas as pd

PUNCTUATION = string.punctuation


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


def main():
    df = pd.read_csv('/data4/u5941758/youtube-polarization/prediction/unseen_user_comments.tsv', sep='\t')
    to_store_user_ids = []
    to_store_user_docs = []
    cnt_process = 0
    with open('/data4/u5941758/youtube-polarization/prediction/non_informative_unseen_users.csv', 'w') as fout:
        for x, y in zip(df['user_id'].values, df['user_doc'].values):
            try:
                tmp = normalize(y)
                if len(tmp) > 0:
                    to_store_user_ids.append(x)
                    to_store_user_docs.append(y)
                else:
                    fout.write('{0},{1}\n'.format(x, y))
            except Exception as e:
                fout.write('{0},{1}\n'.format(x, y))

            cnt_process += 1
            if cnt_process % 100000 == 0:
                print('processed {0:,} users'.format(cnt_process))

    print('processed {0:,} users'.format(cnt_process))
    # create pandas obj
    data = {'user_id': to_store_user_ids, 'user_doc': to_store_user_docs}
    pd_data = pd.DataFrame.from_dict(data)

    pd_data.to_csv('/data4/u5941758/youtube-polarization/prediction/cleaned_unseen_user_comments.tsv', index=False, sep="\t")


if __name__ == '__main__':
    main()

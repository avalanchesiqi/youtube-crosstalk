import re
from hnatt import HNATT


if __name__ == '__main__':
    SAVED_MODEL_DIR = 'saved_models'

    saved_model_filename = 'cv1_hnatt_model.h5'
    saved_tokenizer_filename = 'cv1_hnatt_model.h5.tokenizer'

    # initialize HNATT
    h = HNATT()
    h.load_weights(SAVED_MODEL_DIR, saved_model_filename, saved_tokenizer_filename)

    # a user posts several comments, each comment consists of several words
    comments = ["It is what it is or they were nevertrumpists so they didn't like me and I don't know them",
                'vote biden to save American',
                'We love #joebiden2020 for President.',
                '#bluewave2020 BUT PREP FOR TRUMP PUTIN CIVIL WAR',
                'trumpvirus came from a sick fatass loser',
                'trump has changed his tune about the corona trumpvirus. because trumpist are kicking the bucket']

    # remove punctuations from each comment, and then join them by dot
    comments = [re.sub(r'[^\w\s]', ' ', x).strip() for x in comments]
    comments = '. '.join(comments)

    prob_lib, prob_con = h.predict_texts(comments)[0]
    if prob_con <= 0.05:
        print('Predicted leaning: Liberal, prob_lib: {0:.4f}, prob_con: {1:.4f}'.format(prob_lib, prob_con))
    elif prob_con >= 0.95:
        print('Predicted leaning: Conservative, prob_lib: {0:.4f}, prob_con: {1:.4f}'.format(prob_lib, prob_con))
    else:
        print('Predicted leaning: Unknown, prob_lib: {0:.4f}, prob_con: {1:.4f}'.format(prob_lib, prob_con))

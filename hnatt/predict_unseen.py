import sys, os, re, json
import util.data as data_loader
from hnatt import HNATT


def str_x(x):
    y = []
    for xx in x:
        x1, x2 = xx
        t = []
        for xx1 in x1:
            t.append('{0},{1}'.format(xx1[0], xx1[1]))
        t.append(str(x2))
        t = ' '.join(t)
        y.append(t)
    y = '+'.join(y)
    return y


if __name__ == '__main__':
    UNSEEN_DATA_PATH = '../prediction/cleaned_unseen_user_comments.tsv'
    SAVED_MODEL_DIR = 'saved_models'

    idx_fold = sys.argv[1]

    saved_model_filename = 'cv{0}_hnatt_model.h5'.format(idx_fold)
    saved_tokenizer_filename = 'cv{0}_hnatt_model.h5.tokenizer'.format(idx_fold)
    unseed_prediction_filename = os.path.join(SAVED_MODEL_DIR, 'unseen{0}_hnatt_prediction.json'.format(idx_fold))

    # initialize HNATT
    h = HNATT()
    h.load_weights(SAVED_MODEL_DIR, saved_model_filename, saved_tokenizer_filename)

    # print attention activation maps across sentences and words per sentence
    text = 'i hate trump. #nevertrump. vote biden to save america.'
    text = re.sub(r'[^\w\s.]', ' ', text).strip()
    # print(h._encode_input(text).shape)
    print(h.predict_texts(text))
    activation_maps = h.activation_maps(text)
    print(activation_maps)

    # unseen dataset
    num_skip = 0
    if os.path.exists(unseed_prediction_filename):
        with open(unseed_prediction_filename, 'r') as fin:
            for line in fin:
                num_skip += 1

    batch_size = 512
    unseen_uid, unseen_token, _ = data_loader.load_unseen_data(path=UNSEEN_DATA_PATH, num_skip=num_skip)
    with open(unseed_prediction_filename, 'a') as fout:
        num_test = len(unseen_uid)
        num_batch = num_test // batch_size + 1
        for batch_idx in range(num_batch):
            batch_start_idx = int(batch_size * batch_idx)
            batch_end_idx = min(int(batch_size * (batch_idx + 1)), num_test)
            batch_uid = unseen_uid[batch_start_idx: batch_end_idx]
            batch_token = unseen_token[batch_start_idx: batch_end_idx]
            batch_preds = h.predict(batch_token)

            for uid, pred in zip(batch_uid, batch_preds):
                ret = {'user_id': uid, 'pred_l': str(pred[0]), 'pred_r': str(pred[1])}
                # print(json.dumps(ret))
                fout.write('{0}\n'.format(json.dumps(ret)))
            if batch_idx % 10 == 0:
                print('finish batch {0}'.format(batch_idx))

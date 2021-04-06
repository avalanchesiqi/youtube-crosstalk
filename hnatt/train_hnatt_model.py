import sys, os, re, json
import util.data as data_loader
from sklearn.metrics import confusion_matrix, accuracy_score
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
    DATA_PATH = '../prediction/cleaned_seed_user_label_comments.tsv'
    SAVED_MODEL_DIR = 'saved_models'
    if not os.path.exists(SAVED_MODEL_DIR):
        os.mkdir(SAVED_MODEL_DIR)
    EMBEDDINGS_PATH = 'glove.6B/glove.6B.100d.txt'
    NUM_FOLD = 5

    idx_fold = 1
    for (train_uid, train_x, train_y, train_text), (test_uid, test_x, test_y, test_text) in data_loader.load_data(path=DATA_PATH, num_fold=NUM_FOLD):
        print('training fold {0}'.format(idx_fold))
        saved_model_filename = 'cv{0}_hnatt_model.h5'.format(idx_fold)
        saved_tokenizer_filename = 'cv{0}_hnatt_model.h5.tokenizer'.format(idx_fold)
        cv_prediction_filename = 'cv{0}_hnatt_prediction.json'.format(idx_fold)

        # initialize HNATT
        h = HNATT()
        h.train(train_x, train_y, batch_size=64, epochs=5, embeddings_path=EMBEDDINGS_PATH,
                saved_model_dir=SAVED_MODEL_DIR, saved_model_filename=saved_model_filename)

        # print attention activation maps across comments and words per comment
        text = 'i hate trump. #nevertrump. vote biden to save america.'
        text = re.sub(r'[^\w\s.]', ' ', text).strip()
        # print(h._encode_input(text).shape)
        print(h.predict_texts(text))
        activation_maps = h.activation_maps(text)
        print(activation_maps)

        test_preds = h.predict(test_x)
        test_y_true = []
        test_y_pred = []
        test_cnt = 0
        with open(os.path.join(SAVED_MODEL_DIR, cv_prediction_filename), 'w') as fout:
            for pred, text, true, uid in zip(test_preds, test_text, test_y, test_uid):
                if test_cnt < 100:
                    text = re.sub(r'[^\w\s.]', ' ', text).strip()
                    h_activation_map = h.activation_maps(text)
                else:
                    h_activation_map = ''
                test_cnt += 1
                if pred[0] > pred[1]:
                    test_y_pred.append(0)
                else:
                    test_y_pred.append(1)
                if true[0] > true[1]:
                    test_y_true.append(0)
                    if len(h_activation_map) > 0:
                        ret = {'user_id': uid, 'true': 0, 'pred_l': str(pred[0]), 'pred_r': str(pred[1]),
                               'amap': str_x(h_activation_map)}
                    else:
                        ret = {'user_id': uid, 'true': 0, 'pred_l': str(pred[0]), 'pred_r': str(pred[1])}
                    # print(json.dumps(ret))
                    fout.write('{0}\n'.format(json.dumps(ret)))
                else:
                    test_y_true.append(1)
                    if len(h_activation_map) > 0:
                        ret = {'user_id': uid, 'true': 1, 'pred_l': str(pred[0]), 'pred_r': str(pred[1]),
                               'amap': str_x(h_activation_map)}
                    else:
                        ret = {'user_id': uid, 'true': 1, 'pred_l': str(pred[0]), 'pred_r': str(pred[1])}
                    # print(json.dumps(ret))
                    fout.write('{0}\n'.format(json.dumps(ret)))
        print('confusion matrix on the test dataset')
        print(confusion_matrix(test_y_true, test_y_pred))
        print('accuracy in fold {0}: {1:.4f}'.format(idx_fold, accuracy_score(test_y_true, test_y_pred)))

        idx_fold += 1

    # # unseen dataset
    # batch_size = 256
    # unseen_uid, unseen_token, unseen_text = data_loader.load_unseen_data(path=UNSEEN_DATA_PATH)
    # unseen_cnt = 0
    # with open('hnatt_prediction_output_unseen.json', 'w') as fout:
    #     num_test = len(unseen_uid)
    #     num_batch = num_test // batch_size + 1
    #     for batch_idx in range(num_batch):
    #         batch_uid = unseen_uid[int(batch_size * batch_idx): min(int(batch_size * (batch_idx + 1)), num_test)]
    #         batch_token = unseen_token[int(batch_size * batch_idx): min(int(batch_size * (batch_idx + 1)), num_test)]
    #         batch_text = unseen_text[int(batch_size * batch_idx): min(int(batch_size * (batch_idx + 1)), num_test)]
    #         batch_preds = h.predict(batch_token)
    #
    #         for uid, text, pred in zip(batch_uid, batch_text, batch_preds):
    #             if unseen_cnt < 100:
    #                 text = re.sub(r'[^\w\s.]', ' ', text).strip()
    #                 h_activation_map = h.activation_maps(text)
    #             else:
    #                 h_activation_map = ''
    #             unseen_cnt += 1
    #             try:
    #                 ret = {'user_id': uid, 'pred_l': str(pred[0]), 'pred_r': str(pred[1]),
    #                        'amap': str_x(h_activation_map)}
    #             except:
    #                 ret = {'user_id': uid, 'pred_l': str(pred[0]), 'pred_r': str(pred[1]), 'amap': ''}
    #             # print(json.dumps(ret))
    #             fout.write('{0}\n'.format(json.dumps(ret)))
    #         print('finish batch {0}'.format(batch_idx))
    #
    # h.load_weights(SAVED_MODEL_DIR, SAVED_MODEL_FILENAME, SAVED_TOKENIZER_FILENAME)
    #
    # # print attention activation maps across sentences and words per sentence
    # text = 'i hate trump. #nevertrump. vote biden to save america.'
    # text = re.sub(r'[^\w\s.]', ' ', text).strip()
    # # print(h._encode_input(text).shape)
    # print(h.predict_texts(text))
    # activation_maps = h.activation_maps(text)
    # print(activation_maps)

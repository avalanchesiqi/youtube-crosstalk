import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import KFold

from util.text_util import normalize

tqdm.pandas()


def chunk_to_arrays(chunk):
	x = chunk['user_id'].values
	y = chunk['text_tokens'].values
	z = chunk['user_doc'].values
	w = chunk['user_label'].values
	return x, y, z, w


def chunk_to_arrays_test(chunk):
	x = chunk['user_id'].values
	y = chunk['text_tokens'].values
	z = chunk['user_doc'].values
	return x, y, z


def balance_classes(x, y, train_ratio):
	x_negative = x[np.where(y == 0)]
	y_negative = y[np.where(y == 0)]
	x_positive = x[np.where(y == 1)]
	y_positive = y[np.where(y == 1)]

	n = min(len(x_negative), len(x_positive))
	train_n = int(train_ratio * n)
	train_x = np.concatenate((x_negative[:train_n], x_positive[:train_n]), axis=0)
	train_y = np.concatenate((y_negative[:train_n], y_positive[:train_n]), axis=0)
	test_x = np.concatenate((x_negative[train_n:], x_positive[train_n:]), axis=0)
	test_y = np.concatenate((y_negative[train_n:], y_positive[train_n:]), axis=0)

	# import pdb; pdb.set_trace()
	return (train_x, to_one_hot(train_y, dim=2)), (test_x, to_one_hot(test_y, dim=2))


def to_one_hot(labels, dim=2):
	results = np.zeros((len(labels), dim))
	for i, label in enumerate(labels):
		results[i][label] = 1
	return results


def load_data(path, nrows=None, num_fold=5, train_ratio=0.8):
	print('loading data...')
	if nrows is None:
		df = pd.read_csv(path, sep='\t', usecols=['user_id', 'user_label', 'user_doc'])
	else:
		df = pd.read_csv(path, nrows=nrows, sep='\t', usecols=['user_id', 'user_label', 'user_doc'])
	# df = df.sample(frac=1, random_state=42).reset_index(drop=True)
	df['text_tokens'] = df['user_doc'].progress_apply(lambda x: normalize(x))

	size = df.shape[0]
	kf = KFold(n_splits=num_fold, shuffle=True, random_state=57)

	for train_index, test_index in kf.split(np.arange(size)):
		train_set = df.iloc[train_index].copy()
		train_uid, train_x, train_text, train_y = chunk_to_arrays(train_set)
		train_left = train_y[np.where(train_y == 0)]
		train_right = train_y[np.where(train_y == 1)]
		print('\n{0} left and {1} right in train'.format(len(train_left), len(train_right)))
		train_y = to_one_hot(train_y)

		test_set = df.iloc[test_index]
		test_uid, test_x, test_text, test_y = chunk_to_arrays(test_set)
		test_left = test_y[np.where(test_y == 0)]
		test_right = test_y[np.where(test_y == 1)]
		print('{0} left and {1} right in test'.format(len(test_left), len(test_right)))
		test_y = to_one_hot(test_y)

		yield (train_uid, train_x, train_y, train_text), (test_uid, test_x, test_y, test_text)


def load_unseen_data(path, num_skip=0, nrows=None):
	print('loading unseen data...')
	if nrows is None and num_skip == 0:
		df = pd.read_csv(path, sep='\t', usecols=['user_id', 'user_doc'])
	elif nrows is not None and num_skip == 0:
		df = pd.read_csv(path, nrows=nrows, sep='\t', usecols=['user_id', 'user_doc'])
	elif nrows is None and num_skip > 0:
		df = pd.read_csv(path, skiprows=range(1, num_skip), sep='\t', usecols=['user_id', 'user_doc'])
	else:
		print('nrows and skiprows cannot be used together! exit...')
		sys.exit(1)

	df['text_tokens'] = df['user_doc'].progress_apply(lambda x: normalize(x))

	uid, tokens, text = chunk_to_arrays_test(df)
	print('finished loading test dataset...')

	return uid, tokens, text

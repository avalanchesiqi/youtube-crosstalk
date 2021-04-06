import re
import numpy as np

from flask import Flask
from flask import render_template
from flask import request
from flask import Response
from flask import jsonify
import tensorflow as tf
from keras import backend as K

from util import text_util
from hnatt2 import HNATT

SAVED_MODEL_DIR = 'saved_models'
SAVED_MODEL_FILENAME = 'yt_model.h5'
SAVED_TOKENIZER_FILENAME = 'yt_model.h5.tokenizer'

app = Flask(__name__)

K.clear_session()
h = HNATT()
h.load_weights(SAVED_MODEL_DIR, SAVED_MODEL_FILENAME, SAVED_TOKENIZER_FILENAME)
graph = tf.get_default_graph()

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/activations')
def activations():
	"""
	Receive a text and return HNATT activation map
	"""
	if request.method == 'GET':
		text = request.args.get('text', '')
		if len(text.strip()) == 0:
			return Response(status=400)

		text = re.sub(r'[^\w\s.]', ' ', text).strip()

		global graph
		with graph.as_default():
			activation_maps = h.activation_maps(text, websafe=True)
			print(activation_maps)
			print(text.split('.'))
			preds = h.predict_text([text])[0]
			print(preds)
			prediction = np.argmax(preds).astype(float)
			data = {
				'activations': activation_maps,
				'normalizedText': text.split('.'),
				'prediction': prediction,
				'binary': True
			}
			return jsonify(data)
	else:
		return Response(status=501)
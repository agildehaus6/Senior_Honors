from flask import Flask
from flask import request

app = Flask(__name__)

import predict_app.src.training.Parsing.builder_detailed as parser
import predict_app.src.evaluation.evaluate as evaluator

MODEL_PATH = 'predict_app/src/resources/model_weights/model_weights.h5'


def handle_req(data):
    json_data = request.get_json()
    print("\nRaw graph json data:\n")
    print(json_data)
    nodes, edges = parser.parse_json_post(json_data)
    print("\nAll Nodes Encoded for prediction:\n")
    print(nodes)
    print("\nAll edges encoded for prediction:\n")
    print(edges)
    return evaluator.predict(nodes, edges, MODEL_PATH)


@app.route('/')
def index():
    return 'Index'


@app.route('/predict_1')
def predict():
    return 'Predict'


@app.route('/predict', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        json_data = request.get_json()
        response = handle_req(json_data)
        return str(response)
    else:
        return "Please post a json file"


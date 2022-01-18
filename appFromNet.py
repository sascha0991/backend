from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

converted_data = "trololo"


@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Expose-Headers'] = '*'
    return response


@app.route("/")
def hello():
    return jsonify({"data": "Hello, World!"}), 200


def convert_json():
    data_from_csv = pd.read_csv("csv_files\\peerGraph_07-11-21.csv", delimiter=';')
    iter = 0
    count = 1
    data_to_json = {}
    data_to_json['nodes'] = []
    data_to_json['links'] = []
    nodes_ids = {}

    for src in data_from_csv['SOURCE']:
        if(not str(src) in nodes_ids):
            nodes_ids[str(src)] = str(count)
            data_to_json['nodes'].append({
                'id': str(count)
            })
            count += 1
        if(not str(data_from_csv['TARGET'][iter]) in nodes_ids):
            nodes_ids[str(data_from_csv['TARGET'][iter])] = str(count)
            data_to_json['nodes'].append({
                'id': str(count)
            })
            count += 1
        iter += 1

    iter = 0
    for src in data_from_csv['SOURCE']:
        data_to_json['links'].append({
            'sid': nodes_ids[str(src)],
            'tid': nodes_ids[str(data_from_csv['TARGET'][iter])]
        })
        iter += 1

    return data_to_json


@app.route("/json")
def get_json():
    return jsonify({"data": converted_data}), 200


@app.route("/nodes")
def get_nodes():
    return jsonify({"nodes": converted_data['nodes'][:10]}), 200


@app.route("/links")
def get_links():
    return jsonify({"links": converted_data['links'][:100]}), 200


@app.route("/upload", methods=['POST'])
def load_csv():
    if 'file' not in request.files:
        print('No file part')
    file = request.files['file']
    print("enter load_csv")
    print(file)
    global converted_data
    converted_data = convert_json(request.files['file_csv'])
    print("file_csv: ", request.files['file_csv'])


if __name__ == "__main__":
    converted_data = convert_json()
    app.run(host='0.0.0.0', port=5000, debug=True)

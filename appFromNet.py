from flask import Flask, jsonify, Response, make_response, send_file
import pandas as pd
import igraph as ig
import cv2


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


def convert_json(data_from_csv, nodes_ids):
    data_to_json = {}
    data_to_json['nodes'] = []
    data_to_json['links'] = []

    for nd in nodes_ids:
        data_to_json['nodes'].append({
            'id': str(nodes_ids[nd])
        })

    for src, trg in zip(data_from_csv['SOURCE'], data_from_csv['TARGET']):
        data_to_json['links'].append({
            'sid': nodes_ids[src],
            'tid': nodes_ids[trg]
        })

    return data_to_json


def select_data(data_from_csv, nodes_ids, node=0):
    data_to_json = {'nodes': [], 'links': []}
    node_id = ""
    selected_nodes = []

    for nd in nodes_ids:
        if nodes_ids[nd] == node:
            node_id = nd
            break

    if node_id != "":
        subgraph = data_from_csv.loc[data_from_csv['SOURCE'] == node_id]
        data_to_json['nodes'].append({
            'id': str(nodes_ids[node_id])
        })
        for trg in subgraph['TARGET']:
            data_to_json['links'].append({
                'sid': str(nodes_ids[node_id]),
                'tid': str(nodes_ids[trg])
            })
            if trg not in selected_nodes:
                selected_nodes.append(trg)
                data_to_json['nodes'].append({
                    'id': str(nodes_ids[trg])
                })

    visited_nodes = selected_nodes.copy()
    for nd_id in selected_nodes:
        subgraph = data_from_csv.loc[data_from_csv['SOURCE'] == nd_id]
        iter = 0
        for trg in subgraph['TARGET']:
            if iter == 2:
                break
            data_to_json['links'].append({
                'sid': str(nodes_ids[nd_id]),
                'tid': str(nodes_ids[trg])
            })
            if trg not in visited_nodes:
                visited_nodes.append(trg)
                data_to_json['nodes'].append({
                    'id': str(nodes_ids[trg])
                })
            iter += 1

    return data_to_json


def create_png(data_from_csv, nodes_ids):
    links = []

    for src, trg in zip(data_from_csv['SOURCE'], data_from_csv['TARGET']):
        links.append((nodes_ids[str(src)], nodes_ids[str(trg)]))

    g = ig.Graph(links)
    layout = g.layout("lgl")
    visual_style = {"vertex_size": 10, "vertex_color": "red", "layout": layout, "bbox": (1000, 1000), "margin": 20}
    ig.plot(g, "network.png", **visual_style)
    return


@app.route('/image')
def get_image(pid="network.png"):
    return send_file(pid, mimetype='image/png')


def create_map_nodes_ids(data_from_csv):
    count = 0
    nodes_ids = {}

    for src, trg in zip(data_from_csv['SOURCE'], data_from_csv['TARGET']):
        if src not in nodes_ids:
            nodes_ids[src] = count
            count += 1
        if trg not in nodes_ids:
            nodes_ids[trg] = count
            count += 1

    return nodes_ids


@app.route("/json")
def get_json():
    return jsonify({"data": converted_data}), 200


@app.route("/nodes")
def get_nodes():
    return jsonify({"nodes": converted_data['nodes']}), 200


@app.route("/links")
def get_links():
    return jsonify({"links": converted_data['links']}), 200


if __name__ == "__main__":
    data_from_csv = pd.read_csv("csv_files\\peerGraph_07-11-21.csv", delimiter=';')
    nodes_ids = create_map_nodes_ids(data_from_csv)
    create_png(data_from_csv, nodes_ids)
#    converted_data = convert_json(data_from_csv, nodes_ids)
    converted_data = select_data(data_from_csv, nodes_ids, 0)
    app.run(host='0.0.0.0', port=5000, debug=True)

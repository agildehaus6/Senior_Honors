import json
import glob
import os

data_path = "../../resources/raw_data/dbyd/"
outpath = "../../resources/data/aifdb/"

outpath_testing = "../../resources/testing_data/"


def read_json(file_id):
    json_file = open(data_path +"nodeset"+ file_id + ".json")
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data


def get_nodes(json_data, file_id):
    raw_nodes = json_data["nodes"]
    parsed_nodes = {}
    for node in raw_nodes:
        if (node["type"] == "RA") | (node["type"] == "CA"):
            parsed_nodes[file_id + node["nodeID"]] = node["type"]
    return parsed_nodes


def get_edges(json_data, file_id, nodes):
    raw_edges = json_data["edges"]
    edge_holder = {}
    parsed_edges = []
    for edge in raw_edges:
        edge_holder[edge["fromID"]] = edge["toID"]

    for fromId, toId in edge_holder.items():
        # print(fromId, toId)
        if(file_id+fromId) in nodes:
            valid_tos = get_valid_to(toId, file_id, edge_holder, nodes)
            for to in valid_tos:
                parsed_edges.append((file_id+fromId, file_id+to))
    # print(parsed_edges)
    return parsed_edges


def get_valid_to(node_id, file_id, edge_holder, nodes):
    valid_nodes = []
    for fromId, toId in edge_holder.items():
        if (fromId == node_id) & (file_id+toId in nodes):
            valid_nodes.append(toId)
    return valid_nodes


def write_file(nodes_fn, edges_fn, file_id, data):
    nodes_file = open(nodes_fn, "a+")
    edges_file = open(edges_fn, "a+")
    all_nodes = get_nodes(data, file_id)
    all_edges = get_edges(data,file_id,all_nodes)

    # 10 is pro, 01 is con
    for key, type in all_nodes.items():
        if type == "RA":
            entry = build_content_entry(key, all_nodes, all_edges, "RA")
            print(entry)
            nodes_file.write(entry + "\n")
        else:
            entry = build_content_entry(key, all_nodes, all_edges, "CA")
            print(entry)
            nodes_file.write(entry + "\n")
    for edge in all_edges:
        edges_file.write(str(edge[0]) + "  " + str(edge[1]) + "\n")

    nodes_file.close()
    edges_file.close()


def build_content_entry(node_key, nodes, edges, type):
    parents = []
    children = []
    # Add all children of node to
    for edge in edges:
        if edge[0] == node_key:
            children.append({"key": edge[1], "type": ""})
            # Add to children
        if edge[1] == node_key:
            parents.append({"key": edge[0], "type": ""})

    for parent in parents:
        for all_key, all_type in nodes.items():
            if all_key == parent["key"]:
                parent["type"] = all_type
    for child in children:
        for all_key, all_type in nodes.items():
            if all_key == child["key"]:
                child["type"] = all_type

    # Add features
    entry = node_key
    parents_seen = 0
    for parent in parents:
        if parent["type"] == "CA":
            entry += " 0 1"
        else:
            entry += " 1 0"
        parents_seen += 1

    for i in range(parents_seen, 30):
        entry += " 0 0"
        i+=1

    #Add type
    entry += " " + type

    for child in children:
        encoding = "00"
        if child["type"] == "CA":
            encoding = "01"
        else: encoding = "10"
        #entry += encoding

    return entry


def build_file(all):
    if all != 0:
        print("Building")
        for filename in glob.glob(os.path.join(data_path, '*.json')):
            print("\n " + filename)
            split = filename.split("nodeset")
            file_id = split[1].split(".")[0]
            data = read_json(file_id)
            write_file(outpath+"aifdb.content", outpath+"aifdb.cites", file_id, data)

    else:
        print("TESTING")
        filename = "nodeset9279.json"
        split = filename.split("nodeset")
        file_id = split[1].split(".")[0]
        data = read_json(file_id)
        write_file(outpath_testing + "eval_testing.content", outpath_testing + "eval_testing.cites", file_id, data)


b_type = 1

#build_file(b_type)
build_file(b_type)

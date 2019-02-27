from src.training.utils import *
from keras import Model
from keras.layers import Input, Dropout
from kegra.layers.graph import GraphConvolution
from keras.optimizers import Adam
from keras.regularizers import l2

#build_file(0)

# Define parameters
DATASET = 'eval_testing'
FILTER = 'localpool'  # 'chebyshev'
MAX_DEGREE = 2  # maximum polynomial degree
SYM_NORM = True  # symmetric (True) vs. left-only (False) normalization
NB_EPOCH = 200
PATIENCE = 10  # early stopping patience


def load_data_eval(path="../resources/testing_data/", dataset="no bad"):
    print('Loading {} dataset...'.format(dataset))

    idx_features_labels = np.genfromtxt("{}{}.content".format(path, dataset), dtype=np.dtype(str))
    features = sp.csr_matrix(idx_features_labels[:, 1:-1], dtype=np.float32)
    labels = encode_onehot(idx_features_labels[:, -1])

    # build graph
    idx = np.array(idx_features_labels[:, 0], dtype=np.int32)
    idx_map = {j: i for i, j in enumerate(idx)}
    edges_unordered = np.genfromtxt("{}{}.cites".format(path, dataset), dtype=np.int32)
    edges = np.array(list(map(idx_map.get, edges_unordered.flatten())),
                     dtype=np.int32).reshape(edges_unordered.shape)
    adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:, 0], edges[:, 1])),
                        shape=(labels.shape[0], labels.shape[0]), dtype=np.float32)

    # build symmetric adjacency matrix
    adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)

    print('Dataset has {} nodes, {} edges, {} features.'.format(adj.shape[0], edges.shape[0], features.shape[1]))

    return features.todense(), adj, labels


def predict():
    X, A, y = load_data_eval(dataset=DATASET)


    A_ = preprocess_adj(A, SYM_NORM)
    support = 1
    graph = [X, A_]
    G = [Input(shape=(None, None), batch_shape=(None, None), sparse=True)]

    X_in = Input(shape=(X.shape[1],))

    H = Dropout(0.5)(X_in)
    H = GraphConvolution(16, support, activation='relu', kernel_regularizer=l2(5e-4))([H]+G)
    H = Dropout(0.5)(H)
    Y = GraphConvolution(y.shape[1], support, activation='softmax')([H]+G)


    # Recreate the exact same model, including weights and optimizer.
    model2 = Model(inputs=[X_in]+G, outputs=Y)
    model2.compile(loss='categorical_crossentropy', optimizer=Adam(lr=0.01))

    model2.load_weights('../model_weights/model_weights.h5', by_name=True)

    preds = model2.predict(graph, batch_size=A.shape[0])
    print(preds)
    return preds

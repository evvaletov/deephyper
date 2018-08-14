from collections import OrderedDict

from deephyper.search.models.base import param, step
class Problem():
    def __init__(self):
        self.space = [
            param.discrete('epochs', 5, 500),
            param.non_ordinal('rnn_type', ['LSTM', 'GRU', 'SimpleRNN']),
            param.discrete('nhidden', 1, 100),
            param.discrete('nlayers', 1, 30),
            param.non_ordinal('activation', ['relu', 'elu', 'selu', 'tanh']),
            param.discrete('batch_size', 8, 1024, step.GEOMETRIC, 2),
            param.continuous('dropout', 0, 1),
            param.non_ordinal('optimizer', ['sgd', 'rmsprop', 'adagrad',
                                            'adadelta', 'adam', 'adamax',
                                            'nadam']),
            param.continuous('learning_rate', 1e-04, 1e01)
        ]
        # space = OrderedDict()
        # space['epochs'] = (5, 500)
        # #bechmark specific parameters
        # space['rnn_type'] = ['LSTM', 'GRU', 'SimpleRNN']
        # space['nhidden'] = (1, 100)
        # space['nlayers'] = (1, 30)
        # #network parameters
        # space['activation'] = ['relu', 'elu', 'selu', 'tanh']
        # space['batch_size'] = (8, 1024)
        # space['dropout'] = (0.0, 1.0)
        # space['optimizer'] = ['sgd', 'rmsprop', 'adagrad', 'adadelta', 'adam', 'adamax', 'nadam']
        # #space['init'] = ['Zeros', 'Ones', 'Constant', 'RandomNormal', 'RandomUniform', 'TruncatedNormal', 'VarianceScaling', 'Orthogonal', 'Identity', 'lecun_uniform', 'glorot_normal', 'glorot_uniform', 'he_normal', 'lecun_normal', 'he_uniform']
        # # common optimizer parameters
        # #space['clipnorm'] = (1e-04, 1e01)
        # #space['clipvalue'] = (1e-04, 1e01)
        # # optimizer parameters
        # space['learning_rate'] = (1e-04, 1e01)
        # #space['patience'] = (5, 100)
        # #space['delta'] = (0, 1e-02)
        # #space['momentum'] =  (0, 1e01)
        # #space['decay'] =  (0, 1e01)
        # #space['nesterov'] = [False, True]
        # #space['rho'] = (1e-04, 1e01)
        # #space['epsilon'] = (1e-08, 1e01)
        # #space['beta1'] = (1e-04, 1e01)
        # #space['beta2'] = (1e-04, 1e01)
        # self.space = space
        self.params = [param.name for param in self.space]
        self.starting_point = [5, 'LSTM', 1, 1, 'relu', 8, 0.0, 'sgd', 1e-04] #, 5, 0] #, 1.0, 0.5, 0.01, 0, 0, False, 0.9, 1e-08, 0.9, 0.999]

if __name__ == '__main__':
    instance = Problem()
    print(' '.join(f'--{k}={instance.starting_point[i]}' for i,k in enumerate(instance.params)))
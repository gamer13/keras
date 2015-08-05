import caffe_pb2 as caffe
import google.protobuf
from converters import model_from_config, model_from_param, convert_weights


def caffe_to_keras(prototext=None, caffemodel=None, phase='train'):
        '''
            prototext: model description file in caffe
            caffemodel: stored weights file
            phase: train or test
            Usage:
                model_data = caffe_to_keras(prototext='VGG16.prototxt',
                                            caffemodel='VGG16_700iter.caffemodel')
                graph = model_data.get('network') # loaded with with weights is caffemodel is provided, else randomly initialized
                inputs = model_data.get('inputs')
                outputs = model_data.get('outputs')
                weights = model_data.get('weights') # useful for embedding networks
        '''
        model_data = {}

        if prototext:
            config = caffe.NetParameter()
            google.protobuf.text_format.Merge(open(prototext).read(), config)
            print('config')
            print(config)

            input_dim = config.input_dim
            config_layers = config.layers[:]
            network, inputs, outputs = model_from_config(config_layers,
                                                         0 if phase == 'train' else 1,
                                                         input_dim[1:])
        if caffemodel:
            param = caffe.NetParameter()
            param.MergeFromString(open(caffemodel, 'rb').read())
            # print('param')
            # print(param)
            param_layers = param.layers[:]
            if prototext:
                # network already created with prototext
                # see if weights have to be loaded
                weights = convert_weights(param_layers)
                model_data['weights'] = weights
                for layer_weights in weights:
                    network.nodes[layer_weights] = weights[layer_weights]
            else:
                network, inputs, outputs = model_from_param(param_layers)
        model_data['network'] = network
        model_data['inputs'] = inputs
        model_data['outputs'] = outputs
        return model_data
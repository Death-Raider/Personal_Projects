import numpy as np

class DeepFeedForwardNetwork:
    def __init__(self, num_inp: int, num_hidden: list[int], num_out: int):
        self.num_inp = num_inp
        self.num_out = num_out
        self.arch = [num_inp] + num_hidden + [num_out]
        self.activation:list[function] = [lambda x: x]*(len(self.arch)-1) # initilize linear activation
        self.weights:list[np.ndarray] = [np.ndarray((1))]*(len(self.arch)-1)
        self.bias:list = [np.ndarray((1))]*(len(self.arch)-1)
        self.set_weights(None)
        self.set_bias(None)

    def set_bias(self,bias:list[np.ndarray]|None)->None:
        if not bias:
            for i in range(len(self.arch)-1):
                self.bias[i] = np.random.rand(self.arch[i+1])
        else:
            assert len(self.bias) == len(bias)
            for i in range(len(self.bias)):
                assert self.bias[i].shape == bias[i].shape
            
            for i in range(len(self.bias)):
                self.bias[i] = bias[i].copy()

    def set_weights(self,weights:list[np.ndarray]|None)->None:
        if not weights:
            for i in range(len(self.arch)-1):
                self.weights[i] = np.random.rand(self.arch[i],self.arch[i+1])
        else:
            assert len(self.weights) == len(weights)
            for i in range(len(self.weights)):
                assert self.weights[i].shape == weights[i].shape
            
            for i in range(len(self.weights)):
                self.weights[i] = weights[i].copy()

    def get_weights(self)->list[np.ndarray]:
        return self.weights.copy()
    
    def forward_pass(self,inputs: np.ndarray):
        assert inputs.shape == (self.num_inp,)
        result = inputs.copy()
        for i in range(len(self.weights)):
            result = self.activation[i](result @ self.weights[i] + self.bias[i])
        return result

def relu_activation(x:np.ndarray):
    return np.where(x > 0, x, 0)

def leaky_relu_activation(x:np.ndarray):
    return np.where(x > 0, x, 0.01*x)

def sigmoid_activation(x:np.ndarray):
    exp = np.exp(x)
    return exp/(1+exp)

class DQAgent:
    def __init__(self):
        pass

if __name__ == '__main__':
    print("Running DeepFeedForwardNetwork with architecture 3-1-2")
    network = DeepFeedForwardNetwork(3,[1],2)
    print("setting hidden activation as leaky relu")
    network.activation[0] = leaky_relu_activation
    print("setting output activation as sigmoid")
    network.activation[1] = sigmoid_activation
    print("network weight details")
    print(len(network.weights),list(map(lambda x: x.shape, network.weights)))
    print(*network.weights,sep='\n')
    print("network bias details")
    print(network.bias)
    inp = np.array([1,1,0])
    print("inp:", inp, inp.shape)
    print("output:", network.forward_pass(inp))

    print("Re-randomizing weights and bias")
    network.set_bias(None)
    network.set_weights(None)
    print("output:", network.forward_pass(inp))
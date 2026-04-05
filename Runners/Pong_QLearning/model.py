from keras.models import Model
from keras.layers import Dense, Input, BatchNormalization, Dropout, Reshape, MultiHeadAttention, LayerNormalization, Flatten, Concatenate

def model_fn(state_dim, action_dim):
    inputs = Input(shape=(state_dim,))
    x = Dense(32, activation='relu')(inputs)
    y = Dense(32, activation='tanh')(inputs)
    z = Concatenate()([x, y])
    x = Dense(32, activation='tanh')(z)
    outputs = Dense(action_dim, activation='linear')(x)
    return Model(inputs=inputs, outputs=outputs)
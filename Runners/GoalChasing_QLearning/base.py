from keras.layers import Dense, Input, BatchNormalization, Dropout, Reshape, MultiHeadAttention, LayerNormalization, Flatten, Concatenate
from keras.models import Model

def build_model(self):
    per_token_features = 2
    global_features = 2

    grid_size = (self.state_dim - global_features) // per_token_features

    inputs = Input(shape=(self.state_dim,))

    # Split into local tokens and global features
    local_tokens = inputs[:, :grid_size * per_token_features]
    global_feats = inputs[:, grid_size * per_token_features:]

    # Reshape local tokens for attention: (batch, tokens, features)
    x = Reshape((grid_size, per_token_features))(local_tokens)

    # Multi-head self-attention
    attention_out = MultiHeadAttention(num_heads=2, key_dim=8)(x, x, x)
    x = LayerNormalization()(x + attention_out)

    # Flatten attention output
    x = Flatten()(x)

    # Concatenate with global features
    x = Concatenate()([x, global_feats])

    # Dense layers
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    x = Dense(64, activation='relu')(x)
    outputs = Dense(self.action_dim, activation='linear')(x)

    return Model(inputs=inputs, outputs=outputs)
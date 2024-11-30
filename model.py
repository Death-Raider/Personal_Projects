import tensorflow as tf
import keras
from keras import layers
from keras.utils import plot_model


def conv_feature_block(inp,f=8,n=2): # Feature Extraction 
    y = layers.Conv2D(f,(1,1),activation='relu',padding="same")(inp)
    x = layers.Conv2D(f,(5,5),activation='relu',padding="same")(inp)
    for i in range(n):
        x = layers.Conv2D(f,(3,3),activation='relu',padding="same")(x)
    z = layers.Conv2D(f,(5,5),activation='relu',padding="same")(x+y)
    return z
    
def localization_block(inp,f): # small UNET for localization
    x = layers.Conv2D(f,(3,3),activation='relu',padding="same")(inp)
    x_s = layers.MaxPool2D((2,2))(x)
    y = layers.Conv2D(f,(3,3),activation='relu',padding="same")(x_s)
    y = layers.Conv2D(f,(3,3),activation='relu',padding="same")(y)
    x_b = layers.UpSampling2D((2,2))(y)
    z = layers.Conv2D(f,(3,3),activation='relu',padding="same")(x_b+x)
    return z

def conv_reduction_block(inp,f,n=3): # feature distillation using convolution
    x = layers.Conv2D(f, (3,3), activation="relu")(inp)
    for i in range(n-1):
        x = layers.Conv2D(f, (3,3), activation="relu")(x)
    return x

def pooling_reduction_block(inp,f=8,k=(3,3),n=1):
    x = layers.Conv2D(f, k, activation="relu", padding="same")(inp)
    x = layers.MaxPooling2D((2, 2))(x)
    for i in range(n-1):
        x = layers.Conv2D(f, k, activation="relu", padding="same")(x)
        x = layers.MaxPooling2D((2, 2))(x)
    return x

def create_fruit_calorie_model(input_shape=(1000, 1000, 3),out_shape=2):

    # basic model
    input_layer = keras.Input(shape=input_shape)

    x = conv_feature_block(input_layer,f=8,n=2)
    x = pooling_reduction_block(x,f=8,n=1)
    
    x = conv_feature_block(x,f=8,n=2)
    x = pooling_reduction_block(x,f=8,n=1)

    x = conv_feature_block(x,f=16,n=2)
    x = pooling_reduction_block(x,f=16,n=1)

    x = conv_reduction_block(x,f=16,n=4)
    x = pooling_reduction_block(x,f=16,n=1)

    x = conv_reduction_block(x,f=16,n=4)
    x = pooling_reduction_block(x,f=16,n=1)

    x = layers.Flatten()(x)
    x = layers.Dense(500,activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(120,activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(out_shape,activation='relu')(x)

    model = keras.Model(inputs=input_layer, outputs=outputs)

    model.compile(loss="mse", optimizer="adam", metrics=["mae"])  # Compile with mean squared error loss and mean absolute error metric
    model.summary()
    plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
    return model

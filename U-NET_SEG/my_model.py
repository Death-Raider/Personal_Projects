import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow_examples.models.pix2pix import pix2pix
from tensorflow.python.ops import math_ops
from IPython.display import clear_output
import matplotlib.pyplot as plt
import mob_dataset
from PIL import Image
import numpy as np

#---------------Dataset Processing Functions----------------------
def normalize(input_image):
    input_image = tf.cast(input_image, tf.float32) / 255.0
    return input_image

def load_image(data):
    image = normalize(tf.image.resize(data['image'], (224, 224)))
    mask_path = data['mask']
    return image[:,:,:3], mask_path

def process_mask_path(_ ,mask_path):
    mask = np.zeros((224,224,21))
    for i in range(21):
        img = Image.open(f"mob_dataset\\{bytes.decode(mask_path.numpy())}\\{i}.png").convert(mode="L").resize((224,224))
        img = np.array(img)
        mask[:,:,i] = img
    return _, normalize(mask)

def fix_shapes(x,y):
    x.set_shape([224,224,3])
    y.set_shape([224,224,21])
    return x,y
#--------------------Dataset Fetching------------------------------
dataset, info = tfds.load('mob_dataset', with_info=True)
TRAIN_LENGTH = info.splits['train'].num_examples
print(info)
print(TRAIN_LENGTH)
BATCH_SIZE = 4
BUFFER_SIZE = 20
STEPS_PER_EPOCH = TRAIN_LENGTH // BATCH_SIZE

train_images = dataset['train'].map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
train_images = train_images.map(lambda x,y: tf.py_function(process_mask_path, [x,y], [tf.float32,tf.float32]), num_parallel_calls=tf.data.AUTOTUNE)
train_images = train_images.map(fix_shapes)

test_images = dataset['test'].map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
test_images = test_images.map(lambda x,y: tf.py_function(process_mask_path, [x,y], [tf.float32,tf.float32]), num_parallel_calls=tf.data.AUTOTUNE)
test_images = test_images.map(fix_shapes)

train_batches = (
    train_images
    .cache()
    .shuffle(BUFFER_SIZE)
    .batch(BATCH_SIZE)
    .repeat()
    .prefetch(buffer_size=tf.data.AUTOTUNE))

test_batches = (
    test_images
    .cache()
    .batch(1)
    .repeat()
    .prefetch(buffer_size=tf.data.AUTOTUNE))

print("batches", train_batches, test_batches)
#-----------------Printing Functions-------------------------------
def display(display_list):
    plt.figure(figsize=(10, 10))

    title = ['Input Image', 'True Mask', 'Predicted Mask']

    for i in range(len(display_list)):
        plt.subplot(1, len(display_list), i+1)
        plt.title(title[i])
        plt.imshow(tf.keras.utils.array_to_img(display_list[i]))
        plt.axis('off')
    plt.show()

for images, masks in train_batches.take(2):
    print(images,masks)
    sample_image, sample_mask = images[0], masks[0]
    display([sample_image, sample_mask[:,:,0:1]])
#--------------------------Model-----------------------------------
def create_unet_model(input_shape, OUTPUT_CLASSES):
    def unet_model(output_channels:int):
        inputs = tf.keras.layers.Input(shape=input_shape)
        # Downsampling through the model
        skips = down_stack(inputs)
        x = skips[-1]
        skips = reversed(skips[:-1])

        # Upsampling and establishing the skip connections
        for up, skip in zip(up_stack, skips):
            x = up(x)
            concat = tf.keras.layers.Concatenate()
            x = concat([x, skip])

        # This is the last layer of the model
        last = tf.keras.layers.Conv2DTranspose(
            filters=output_channels, kernel_size=3, strides=2,
            padding='same')  #64x64 -> 128x128

        x = last(x)
        return tf.keras.Model(inputs=inputs, outputs=x)

    base_model = tf.keras.applications.MobileNetV2(input_shape=input_shape, include_top=False)
    # Use the activations of these layers
    layer_names = [
        'block_1_expand_relu',   # 64x64
        'block_3_expand_relu',   # 32x32
        'block_6_expand_relu',   # 16x16
        'block_13_expand_relu',  # 8x8
        'block_16_project',      # 4x4
    ]
    base_model_outputs = [base_model.get_layer(name).output for name in layer_names]
    # Create the feature extraction model
    down_stack = tf.keras.Model(inputs=base_model.input, outputs=base_model_outputs)
    down_stack.trainable = False

    up_stack = [
        pix2pix.upsample(512, 3),  # 4x4 -> 8x8
        pix2pix.upsample(256, 3),  # 8x8 -> 16x16
        pix2pix.upsample(128, 3),  # 16x16 -> 32x32
        pix2pix.upsample(64, 3),   # 32x32 -> 64x64
    ]

    return unet_model(output_channels=OUTPUT_CLASSES)

# model = create_unet_model([224, 224, 3], 21)
model = tf.keras.models.load_model("net2")

def loss_function(y_true,y_pred):
    J = [ tf.keras.losses.MSE(y_true[:,:,i], y_pred[:,:,i]) for i in range(21) ]
    C = [0.5,1,1,2,3,0,0,1,0,0,0,0,0,2,2,1,1.5,1.5,0.5,0,0] # 0 for classes that arnt yet in the dataset
    Loss = np.sum([J[i]*C[i] for i in range(21)])
    return Loss

model.compile(optimizer='adam',
            loss=loss_function,
            metrics=['accuracy'])

# tf.keras.utils.plot_model(model, show_shapes=True)
#-----------------Fit Functions-----------------------------------
def create_mask(pred_mask):
    pred_mask = pred_mask[..., tf.newaxis]
    return pred_mask
def show_predictions(dataset=None, num=1):
    if dataset:
        for image, mask in dataset.take(num):
            pred_mask = model.predict(image)
            for mu in range(19):
                display([image[0], mask[0,:,:,mu:mu+1], pred_mask[0,:,:,mu:mu+1] ])
    else:
        for mu in range(19):
            display([sample_image, sample_mask[:,:,mu:mu+1], create_mask( model.predict(sample_image[tf.newaxis, ...]))[0,:,:,mu:mu+1,0] ])

class DisplayCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        clear_output(wait=True)
        if epoch%50 == 0 and not epoch == 0 :
            show_predictions()
            print ('\nSample Prediction after epoch {}\n'.format(epoch+1))
#------------------Training----------------------------------------
# show_predictions(test_batches)
EPOCHS = 150
model_history = model.fit_generator(train_batches, epochs=EPOCHS,
                          steps_per_epoch=STEPS_PER_EPOCH,
                          verbose=2,
                          callbacks=[DisplayCallback()],
                          )
#------------------------------------------------------------------
loss = model_history.history['loss']
acc = model_history.history['accuracy']
model.save("net2")

plt.figure()
plt.plot(model_history.epoch, loss, 'r', label='Training loss')
plt.plot(model_history.epoch, acc, 'r', label='Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Loss Value')
plt.legend()
plt.show()

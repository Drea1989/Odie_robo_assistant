import numpy as np

from PIL import Image


def normalized_preprocess_input(x):
    x /= 255.
    x -= 0.5
    x *= 2.
    return x


def imagenet_preprocess_input(x):
    x = x[:, :, :, ::-1]
    x[:, :, :, 0] -= 103.939
    x[:, :, :, 1] -= 116.779
    x[:, :, :, 2] -= 123.68
    return x


MODEL_SPECS = {
    'inception_v3': {
        'target_size': (299, 299),
        'preprocess_input': normalized_preprocess_input,
    },
    'xception': {
        'target_size': (299, 299),
        'preprocess_input': normalized_preprocess_input,
    },
    'mobilenet_v1': {
        'target_size': (224, 224),
        'preprocess_input': normalized_preprocess_input,
    },
    'resnet50': {
        'target_size': (224, 224),
        'preprocess_input': imagenet_preprocess_input,
    },
    'vgg16': {
        'target_size': (224, 224),
        'preprocess_input': imagenet_preprocess_input,
    },
    'vgg19': {
        'target_size': (224, 224),
        'preprocess_input': imagenet_preprocess_input,
    },
}


def load_image(image_path, target_size=None, preprocess_input=None):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    if target_size:
        width_height = (target_size[0], target_size[1])
        if img.size != width_height:
            img = img.resize(width_height)
    image_data = np.asarray(img, dtype=np.float32)
    image_data = np.expand_dims(image_data, axis=0)
    if preprocess_input:
        image_data = preprocess_input(image_data)
    return image_data

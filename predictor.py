from PIL import Image, ImageChops, ImageEnhance
import os
import itertools
import numpy as np

image_size = (128, 128)
class_names = ['fake', 'real']

def convert_to_ela_image(path, quality):
    temp_filename = 'temp_file_name.jpg'
    ela_filename = 'temp_ela.png'
    image = Image.open(path).convert('RGB')
    image.save(temp_filename, 'JPEG', quality = quality)
    temp_image = Image.open(temp_filename)
    ela_image = ImageChops.difference(image, temp_image)
    extrema = ela_image.getextrema()
    ela_image.save(ela_filename)
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff    
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    
    return ela_image
def prepare_image(image_path):
    return np.array(convert_to_ela_image(image_path, 90).resize(image_size)).flatten() / 255.0

def make_prediction(model, real_image_path):
    image = prepare_image(real_image_path)
    image = image.reshape(-1, 128, 128, 3)
    y_pred = model.predict(image)
    y_pred_class = np.argmax(y_pred, axis = 1)[0]
    print(f'Class: {class_names[y_pred_class]} Confidence: {np.amax(y_pred) * 100:0.2f}')
    return class_names[y_pred_class], np.amax(y_pred) * 100
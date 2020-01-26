import os
import io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import webcolors

# The name of the image file to annotate
file_input = os.path.abspath('/Users/anhnguyen/Desktop/iColor/result.jpg')
file_output = os.path.abspath('/Users/anhnguyen/Desktop/iColor/test.jpg')

def detect_properties(imagefile):
    # Instantiates a client
    client = vision.ImageAnnotatorClient.from_service_account_json("/Users/anhnguyen/Desktop/iColor/key.json")

    content = imagefile.read()
    image = types.Image(content=content)
    return client.image_properties(image=image).image_properties_annotation

def closest_colour(requested_colour):
    #calculate square error between each color in data with the color that has been requested
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

def res(image, color, output_filename):
    im = Image.open(image)
    draw = ImageDraw.Draw(im)
    x, y = im.size #width, height

    #vertex = [(round(x / 2) - 300), (round(y / 2) - 300), (round(x / 2) + 300), (round(y / 2) + 300)]
    vertex = [0, 0, 300, 300]
    rgb_color = (int(color.color.red), int(color.color.green), int(color.color.blue))
    draw = ImageDraw.Draw(im)
    draw.rectangle(vertex, fill=rgb_color)
    actual_name, closest_name = get_colour_name(rgb_color)
    if (actual_name != "None"):
        print(closest_name)
    else:
        print(actual_name)
    im.save(output_filename)

def main(filename):
    # color: rgb color representation
    # score: likelihood of being the subject
    # pixel_fraction: fraction of pixels of that color
    with open(filename, 'rb') as image_file:
        props = detect_properties(image_file)
        max_score = 0
        for color in props.dominant_colors.colors:
            if (color.score > max_score):
                subject_color = color
                max_score = color.score
        image_file.seek(0)
        res(image_file, subject_color, file_output)

main(file_input)


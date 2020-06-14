import os
import secrets
from flask import current_app

def save_picture(picture, folder):
    file_hex = secrets.token_hex(10) #produce a random hex value to be used as a filename
    _, extension = os.path.splitext(picture.filename) #get extension name for filename
    file_name = file_hex + extension #attach filename with extension
    absolute_path = os.path.join(current_app.root_path, 'static/' + folder, file_name) #create absolute path so picture can be saved
    picture.save(absolute_path) #save picture to absolute path directory
    return file_name

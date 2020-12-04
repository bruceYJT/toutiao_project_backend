import os

flask_secret_key = "secret?really?yes!"
base = os.path.dirname(os.path.abspath(__file__))
image_upload_folder = os.path.join(base, 'images')
base_url = "http://127.0.0.1:5000/"
from instapy_cli import client

username = 'your_username'
password = 'your_password'
image = 'test.jpg'
text = 'Hello from instapy-cli! #python #instapy'

with client(username, password) as cli:
    cli.upload(image, text)

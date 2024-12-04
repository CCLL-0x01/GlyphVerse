from server import create_server
from config import config

if __name__ == '__main__':
    app = create_server()
    app.run(**config["server"])
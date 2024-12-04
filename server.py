from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import config
from model import knowledge_acquisition

def create_server():
    app = Flask(__name__)
    app.template_folder='./web/dist'
    if config["server"]["debug"]:
        CORS(app)
    
    @app.route('/')
    def index_page():
        return render_template('index.html')
    
    @app.route('/knowledge_acquisition/<character>', methods=['GET'])
    def knowledge_acqusition(character):
        print(character)
        try:
            data = knowledge_acquisition(character)
        except Exception as e:
            return jsonify({
                "code": -1,
                "message": str(e)
            })
        return jsonify({
            "code": 0,
            "message": "success",
            "data": data
        })
    
    return app

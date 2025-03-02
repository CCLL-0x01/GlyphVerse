from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from config import config
from model import knowledge_acquisition, IMGGenerator
from uuid import uuid4
import os.path
from typing import Dict


def create_server():
    app = Flask(
        __name__,
        static_folder="./web/dist",
        template_folder="./web/dist",
        static_url_path="",
    )
    if config["server"]["debug"]:
        CORS(app)
    
    @app.route('/')
    def index():
        return render_template("index.html")

    # @app.route('/<path:filename>')
    # def static_files(file):
    #     return send_from_directory('./web/dist',file)
    
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
    
    @app.route('/upload',methods=['POST'])
    def upload():
        if request.method=='POST':
            f=request.files['file']
            file_uuid=str(uuid4())
            upload_path=os.path.join(os.path.dirname(__file__),'temp',file_uuid+'.png')
            f.save(upload_path)
            return jsonify({
                "code":0,
                "message":"success",
                "uuid":file_uuid,
            })
        return jsonify({
            "code":-1,
            "message":"bad request",
        })

    @app.route('/temp/<path:filename>') # TODO: 安全漏洞
    def serve_temp_file(filename):
        print(filename)
        temp_dir = os.path.join(app.root_path, 'temp')  # 定义 temp 目录的路径
        print(temp_dir)
        return send_from_directory(temp_dir, filename)
    
    app.image_generator_workers={}
    @app.route('/start',methods=['POST'])
    def start():
        try:
            req_json=request.get_json()
            result_img_uuid=str(uuid4())
            img_gen=IMGGenerator(
                req_json["prompts"]["sub_prompt"],
                req_json["prompts"]["surr_prompt"],
                req_json["char_img"],
                req_json["mask"],
                result_img_uuid
            )
            app.image_generator_workers[img_gen.result_img_uuid]=img_gen
            img_gen.run()
            return jsonify({
                "code":0,
                "message":"success",
                "uuid":result_img_uuid,
            })
        except Exception as e:
            return jsonify({
                "code":-1,
                "message":str(e),
            })

    @app.route('/status/<uuid>',methods=['GET'])
    def status(uuid):
        if uuid in app.image_generator_workers:
            return jsonify({
                "code":0,
                "message":"success",
                "status":app.image_generator_workers[uuid].get_status(),
            })
        else:
            return jsonify({
                "code":-1,
                "message":"not found",
            })


    return app

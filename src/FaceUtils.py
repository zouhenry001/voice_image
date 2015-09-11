

import Config
import json
import time
import os
import uuid
import aiohttp
import tornado.gen
import urllib
import Logger
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest


host = 'https://api.projectoxford.ai/asia/face/v0'


@tornado.gen.coroutine
def detect_faces_in_photo(image):
    Logger.debug('in detect_faces')
    
    faces = []
    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': Config.config['face_api_key'],
    }
    
    params = urllib.parse.urlencode({
        # Request parameters
        'analyzesFaceLandmarks': 'false',
        'analyzesAge': 'false',
        'analyzesGender': 'false',
        'analyzesHeadPose': 'false',
    })
    
    try:
        image_file = open(image, 'rb')
        image_bin = image_file.read()
        url = host + "/detections?%s" % params
        client = AsyncHTTPClient()
        Logger.debug('in async')
        response = yield client.fetch(HTTPRequest(url,method = 'POST',headers=headers, body = image_bin))  
        Logger.debug('after response:'+ response)
        
        if response.status == 200:
            data = yield response.read()
            face_json = json.loads(data.decode())
            print(face_json)
            for face in face_json:
                face_unit = ()
                face_unit.append(face['faceId'])
                face_unit.append(face['faceRectangle'])
                
                faces.append(face_unit)
        
    except Exception as e:
        Logger.error("[Errno {0}] {1}".format(e.errno, e.strerror))
        
    finally:
        return faces














if __name__ == '__main__':
    pass
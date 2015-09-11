

import Config
import json
import time
import os
import uuid
import tornado.gen
import urllib
import Logger
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
import MongoHelper


host = 'https://api.projectoxford.ai/asia/face/v0'


@tornado.gen.coroutine
def detect_faces_in_photo(image,userId):
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
            Logger.debug('face_json:'+ face_json)
            faces = get_face_list(face_json,userId)
            return faces
        
    except Exception as e:
        Logger.error("[Errno {0}] {1}".format(e.errno, e.strerror))
        
    finally:
        return faces


@tornado.gen.coroutine
def get_face_list(face_json,userId):
    faces = []
    try:
        for face in face_json:
            face_unit = ()
            true_faceid =''
            similars = yield find_similar_faces(userId, face['faceId'])
            Logger.debug('similars: ' + str(similars))
            for simi in similars:
                conf = simi['confidence']
                if conf >= 0.9:
                    true_faceid = simi['faceId']
                    break    
            if not true_faceid:
                Logger.debug('no face id detected')
                true_faceid = face['faceId']
                yield add_face_to_group(userId, face['faceId'])
            face_unit.append(true_faceid)
            face_unit.append(face['faceRectangle'])
            person = MongoHelper.get_person(userId, face['faceId'])
            if person['name']:
                face_unit.append(person['name'])
            else:
                face_unit.append('No Name')
            faces.append(face_unit)   
            return faces
    except Exception as e:
        Logger.error("[Errno {0}] {1}".format(e.errno, e.strerror))   
    
    return faces


@tornado.gen.coroutine
def find_similar_faces(user_id, face):
    faces_res = []
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': Config.config['face_api_key'],
    }

    body = {'faceId': face, 'faceGroupId': user_id, 'maxNumOfCandidatesReturned':3}
    try:
        url = host + "/findsimilars"
        client = AsyncHTTPClient()
        Logger.debug('in async')
        response = yield client.fetch(HTTPRequest(url,method = 'POST',headers=headers, body = json.dumps(body)))  
        Logger.debug('after response:'+ response)
        if response.status == 200:
            data = yield response.read()
            json_data = json.loads(data.decode())
            faces_res = json_data
            return faces_res
        
    except Exception as e:
        Logger.error("[Errno {0}] {1}".format(e.errno, e.strerror))
        
    return faces_res


@tornado.gen.coroutine
def add_face_to_group(user_id, face):
    res = False
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': Config.config['face_api_key'],
    }
    
    body = {'faces': [{'faceId':face}]}
    
    try:
        url = host + "/facegroups/%s/faces" % user_id
        client = AsyncHTTPClient()
        Logger.debug('in async')
        response = yield client.fetch(HTTPRequest(url,method = 'POST',headers=headers, body = json.dumps(body)))
        res = response.status == 200
        
    finally:
        return res








if __name__ == '__main__':
    pass
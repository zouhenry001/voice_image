

import json
import BaseAuthenticateHandler
import Utils
import MongoHelper
import Logger
from datetime import datetime
import pypinyin
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.concurrent
import tornado.ioloop
import time
from tornado.options import define, options
from src import FaceUtils




class DetectHandler(BaseAuthenticateHandler.BaseAuthenticateHandler):   
    @tornado.gen.coroutine
    def do_post(self):
        result = {'status': False}
        Logger.debug('in DectHandler')
        try:
            userId = self.get_argument('user_id', '')
            token = self.get_argument('token','')
            user = MongoHelper.get_user_by_id(userId)
            if token != user['token']:      #add
                Logger.debug('token wrong')
                return
            
            #上传图片
            path = Utils.get_user_path(userId)    
                    #if self.request.files:
            files = self.request.files['image']
                    # process image file
            if files is None or len(files) == 0:
                self.write(json.dumps(result))
                return
            fileinfo = files[0]
            fname = fileinfo['filename']    
            fh = open(path + "/" + fname, 'wb')
            fh.write(fileinfo['body'])
            Logger.debug('complete upload')       
            faces = yield FaceUtils.detect_faces_in_photo(path + "/" + fname)
            if len(faces) == 0 or len(faces) > 10:
                return
            
            
            result['faces'] = faces
                        
                    
        finally:
            self.write(json.dumps(result))
                
































if __name__ == '__main__':
    pass
#Encoding=UTF8

import tornado.web
import MongoHelper
import json
import Utils

class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        result = {'status': False}
        try:
            user_id = self.get_argument('user_name', '')
            password = self.get_argument('password', '')
            
            if user_id == '' or password == '':
                return
            
            user = MongoHelper.get_user(user_id, password)
            if not user:
                return
            else:
                result['status'] = True
                result['token'] = Utils.generate_access_token(user_id)
                user_token = result['token']
                MongoHelper.update_user_token(user_id,user_token)
                
            
        finally:
            self.write(json.dumps(result))

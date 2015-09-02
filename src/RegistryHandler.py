#Encoding=UTF8

import tornado.web
import MongoHelper
import json
import Utils

class RegistryHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('only post is supported.')
        
    def post(self):
        result = {'status': False}
        try:
            user_id = self.get_argument('user_id', '')
            user_name = self.get_argument('user_name', '')
            password = self.get_argument('password', '')
            lang = self.get_argument('lang', 'zh-CN')
            if user_id == '' or user_name == '' or password == '':
                self.write(json.dumps(result))
                return
            
            user = MongoHelper.get_user_by_id(user_id)
            if user is not None:
                self.write(json.dumps(result))
                return
            
            user = {'user_id': user_id, 'user_name': user_name, 'password': password, 'lang': lang}
            server = MongoHelper.allocate_user_server()
            user['server'] = server
            user['token'] = Utils.generate_access_token(user_id)   #add
            MongoHelper.register_user(user)
            MongoHelper.increase_server_usage(server, 1)
            result['status'] = True
            user["_id"] = ''
            result['user'] = user
            result['token'] = user['token']
#             result['server'] = user['server']    #added by peigang
            
            
        finally:
            self.write(json.dumps(result))

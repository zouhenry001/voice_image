#Encoding=UTF8

import tornado.web
import MongoHelper
import json
import Utils

class BaseAuthenticateHandler(tornado.web.RequestHandler):
    def get(self):
        if self.is_valid():
            self.do_get()
        else:
            self.output_error()
        
    
    def is_valid(self):
        if self.pass_auth():
            return True
        
        token = self.get_argument('token', '')
        user_id = self.get_argument('user_id', '')
        if token == '' or token != Utils.generate_access_token(user_id):
            return False
        else:
            return True
        
    def output_error(self):
        self.write({'status:': False})
    
    def post(self):
        if self.is_valid():
            self.do_post()
        else:
            self.output_error()
          
    def pass_auth(self):
        return False
      
    def do_get(self):
        pass
    
    def do_post(self):
        pass
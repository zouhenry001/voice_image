#Encoding=UTF8

import tornado.web
import MongoHelper
import json
import Utils
import BaseAuthenticateHandler
import NLPTimeConvertor

class SearchHandler(BaseAuthenticateHandler.BaseAuthenticateHandler):
    def post(self):
        result = {'status': False}
        try:
            user_id = self.get_argument('user_id', '')
#             desc = self.get_argument('desc','')   #add
            print('user_id:',user_id)
            rawTag = self.get_argument('tag', '')
            # 我_r 想_v 找_v 去年_nt 夏天_nt 在_p 西雅图_ns 农贸市场_n 的_u 照片_n
            print('rawTag:',rawTag)
            rawLocation = self.get_argument('loc','')
            print('rawLocation:',rawLocation)
            token = self.get_argument('token','')
            user = MongoHelper.get_user_by_id(user_id)
            print('user:',user)
            if token != user['token']:
                self.write(json.dumps(result))
                return
        
            if user_id == '' or rawTag == '':
                self.write(json.dumps(result))
                return

            key_words = rawTag.split(' ')
            print(key_words)
            if key_words is None or len(key_words) == 0:
                self.write(json.dumps(result))
                return
            meaningful = Utils.get_meaningful_keywords(key_words)
            print('meaningful:',meaningful)
            if rawLocation != '': 
                key_location = rawLocation.split(',')
                print('key_locayion:',key_location)
                latitude = float(key_location[0])
                print('latitude:',latitude)
                longitude = float(key_location[1])  
                print('longitude:',longitude)
                key_location_tag = Utils.get_tag_from_rawlocation(key_location)
                print('key_location_tag:',key_location_tag)    
                meaningful.extend(key_location_tag)
            print('meaningful:',meaningful)
#             face_name = Utils.get_human_names(rawTag)
#             face_id = list(MongoHelper.get_similar_persons(user_id,face_name))  
#             if face_id :
#                 meaningful.extend(face_id)
#             object_name = Utils.get_object_keywords(key_words)
#             cv_tags = Utils.translate_tags(object_name)
#             if cv_tags:
#                 meaningful.extend(cv_tags)
            
            time_range = NLPTimeConvertor.time_api(rawTag)
            print('time_range:',time_range)
            if time_range and rawLocation != '':
                Timage = Utils.get_image_by_time(user_id, time_range)    
                Tag_image = Utils.get_images_by_tag_from_Timage(user_id,meaningful,Timage,1)
                image = Utils.sort_by_location(latitude,longitude,Tag_image)
            elif time_range and rawLocation == '':
                Timage = Utils.get_image_by_time(user_id, time_range)
                image = Utils.get_images_by_tag_from_Timage(user_id,meaningful,Timage,0)
            elif not time_range and rawLocation != '':
                Tag_image = Utils.get_images_by_tag(user_id, meaningful,1)
                print('二维list：',Tag_image)
                image = Utils.sort_by_location(latitude,longitude,Tag_image)
            elif not time_range and rawLocation == '':
                image = Utils.get_images_by_tag(user_id, meaningful,0)
                

            print('image:',image)    
            result['status'] = True
            result['image'] = image


        finally:
            self.write(json.dumps(result))

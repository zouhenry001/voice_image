

import json
import BaseAuthenticateHandler
import Utils
import MongoHelper
import Logger
from datetime import datetime
import pypinyin


class UploadHandler(BaseAuthenticateHandler.BaseAuthenticateHandler):   
    def do_post(self):
        result = {'status': False}
        Logger.debug('in upload')
        try:
            userId = self.get_argument('user_id', '')
            rawLocation = self.get_argument('loc','')   #add           
            desc = [self.get_argument('tag', '')]
            rawTags = self.get_argument('tag', '')
            rowTime = self.get_argument('time', '')
            function = self.get_argument('func','')  #
            token = self.get_argument('token','')           #add
            image_name = self.get_argument('image_name','')    #add
            print('image_name:',image_name)
            print('function:',function)
            user = MongoHelper.get_user_by_id(userId)
            if token != user['token']:      #add
                Logger.debug('token wrong')
                return
            ###for images that has uploaded:if this image was existed,then the customer just want to extend image-tags###
            if function == 'UPDATE':
                print('rawTags:',rawTags)
                print('userId:',userId)
                print('image_name:',image_name)
                if not MongoHelper.check_img_exist(userId, image_name):
                    return    
                update_image_tag(rawTags,userId,image_name)
                MongoHelper.update_image_desc_and_status(desc,userId,image_name)  
                result['status'] = True
            
            elif function == 'UPLOAD':    ###for images that has not uploaded###    
                if MongoHelper.check_img_exist(userId, image_name):
                    return 
                print('userId',userId)
                print('rawTags',rawTags)
                try:
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
                finally:
                # filter out meaningful tags
                    key_words = rawTags.split(' ')
                    print('key_words:',key_words)
                    tags = []
                    if key_words is not None and len(key_words) != 0:
                        tags = Utils.get_meaningful_keywords(key_words)
                        print('tags:',tags)
                # split date and time
                    temptime = datetime.strptime(rowTime, '%Y-%m-%d %X %z')
                    time = datetime(temptime.year, temptime.month, temptime.day, temptime.hour, temptime.minute, temptime.second, 17100)
                    
                    
                    key_location = rawLocation.split(',') # '1122, 234, beijing, zhongguan'
                    Logger.debug('key_location: ' + str(key_location))
                    raw_location_tag = []
                    if key_location is not None and len(key_location) > 1:
                        location = Utils.get_location_from_rawlocation(key_location)
                        Logger.debug('location: ' + str(location))
                        raw_location_tag = Utils.get_tag_from_rawlocation(key_location)
                        Logger.debug('raw_location_tag: ' + str(raw_location_tag))
                        tags.extend(raw_location_tag)
                        Logger.debug('tags: ' + str(tags))
                    
                
                    image = {'user_id': userId, 'image_name': fname, 'location':location, 'desc': desc, 'tags': tags, 'time':time, 'processed': False}
                    MongoHelper.save_image(image)
                    Utils.update_time_indexer(userId,image)
    #                 Utils.update_image_indexer(userId, image)
    #                 face_name = Utils.get_human_names(rawTags)
    #                 MongoHelper.update_person_list(userId,face_name)        ##此函数未写
                    result['status'] = True
        finally:
            self.write(json.dumps(result))
            
def update_image_tag(rawTags,userId,image_name):
                key_words = rawTags.split(' ')
                print('key_words:',key_words)
                tags = Utils.get_meaningful_keywords(key_words)
                print('tags:',tags)
                MongoHelper.extend_tags_in_existimage(userId,image_name,tags)
                
    
         
      
# if __name__ == "__main__":
#     
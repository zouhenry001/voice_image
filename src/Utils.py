#Encoding=UTF8

import Config
from hashlib import md5
import os
import MongoHelper
import pickle
import pypinyin
from pymemcache.client.base import Client
from scipy import spatial
import numpy as np
import json
from fuzzywuzzy import fuzz
from datetime import datetime

mc = Client((Config.config['memcached_host'], 11211))

def get_user_path(userId):
    md5ins = md5()
    md5ins.update(userId.encode())
    md5str = md5ins.hexdigest()
    path = Config.config['photo_root'] + md5str[0:2] + "/" + md5str[2:4] + "/" + md5str[4:6] + "/" + userId
    if not os.path.exists(path):
        os.makedirs(path)
    return path
    
def generate_access_token(userId):
#     md5ins = md5()
#     md5ins.update(userId.encode())
#     md5ins.update(Config.config['access_token'])
#     return md5ins.hexdigest()
    return '123'

def get_meaningful_keywords(key_words):
    keys = []
    for k in key_words:
        pair = k.split('_')
        if pair is None or len(pair) < 2:
            continue
        
        if pair[1] in Config.config['meaningful_pos']:
            keys.append(pypinyin.slug(pair[0]))
        
    
    return keys

def get_object_keywords(key_words):
    keys = []
    for k in key_words:
        pair = k.split('_')
        if pair is None or len(pair) < 2:
            continue
        
        if pair[1] in Config.config['object_pos']:
            keys.append(pypinyin.slug(pair[0]))
    return keys

##added by peigang
def get_location_from_rawlocation(key_location):
    location = {}
    location['longitude'] = float(key_location[0])
    location['latitude'] = float(key_location[1])
    return location
        
def get_tag_from_rawlocation(key_location):
    tags = key_location[2:]
    tagpy = []
    for item in tags:
        tagpy.append(pypinyin.slug(item))
    return tagpy
##added by peigang

def get_user_photo_location_indexer(user_id):
    indexer = mc.get(user_id + '_location')
    if indexer is not None:
        return indexer
    
    filename = get_user_path(user_id) + "/" + "loc_indexer.dat"
    with open(filename,'rb') as fp:
        indexer = pickle.load(fp)
        
    mc.set(user_id, indexer)
    return indexer

def get_user_photo_indexer(user_id):
    indexer = mc.get(user_id)
    if indexer is not None:
        return indexer
    
    filename = get_user_path(user_id) + "/" + "indexer.dat"
    if not os.path.exists(filename):
        indexer = {}
    else:
        with open(filename,'rb') as fp:
            indexer = pickle.load(fp)
        
    mc.set(user_id, indexer)
    return indexer
    
def update_user_photo_indexer(user_id, image):
    filename = get_user_path(user_id) + "/" + "indexer.dat"
    indexer = mc.get(user_id)
    if not indexer:
        if not os.path.exists(filename):
            indexer = {}
        else:
            with open(filename,'rb') as fp:
                indexer = pickle.load(fp)
    
    if indexer is None:
        return
    
    tags = image['tags']
    image_name = image['image_name']
    
    for t in tags:
        pt = pypinyin.slug(t)
        photo_list = indexer.get(pt, [])
        photo_list.append(image_name)
        indexer[pt] = photo_list
    
    with open(filename,'wb') as fp:
        pickle.dump(indexer,fp)
    
    mc.set(user_id, indexer)
    return indexer

def search_images_by_tags(user_id, tags):
    images = []
    indexer = get_user_photo_indexer(user_id)
    if not indexer:
        return images
    
    for tag in tags:
        photo_list = indexer[tag]
        images.append(photo_list)
        
    return images

# this function is used to translate natural language to cv tags
# e.g. 小猫 is translated to cat
def translate_tags(tags):
    cv_tags = mc.get('cv_tags')
    if not cv_tags:
        cv_tags = load_cv_tags()
        mc.set('cv_tags', json.dumps(cv_tags))
    else:
        cv_tags = json.loads(cv_tags.decode('utf-8'))
    
    ret = []
    pytags = [pypinyin.slug(w,separator='') for w in tags]
    for tag in pytags:
        cand = cv_tags.get(tag, [])
        ret.extend(cand)
        
    return ret

def load_cv_tags():
    cv_tags = {}
    path = os.path.dirname(os.path.realpath(__file__)) + "/category.txt"
    if not os.path.exists(path):
        return {}
    
    file = open(path, encoding="utf-8")
    for line in file:
        items = line.strip().split(':')
        tag = items[0]
        words = [pypinyin.slug(w,separator='') for w in items[1].split('-')]
        for word in words:
            if not word in cv_tags.keys():
                cv_tags[word] = []
            cv_tags[word].append(tag)
    
    return cv_tags
        

def get_closest_points(user_id, point):
    indexer = get_user_photo_location_indexer(user_id)
    if not indexer:
        return None
    
    pts = np.array(indexer[0])
    tree = spatial.KDTree(pts)
    res = tree.query(point, k=len(indexer[1]))
    
    print(res)

def get_human_names(raw):
    keys = []
    key_words = raw.split(' ')
    if key_words is None or len(key_words) == 0:
        return
    
    for k in key_words:
        pair = k.split('_')
        if pair is None or len(pair) < 2:
            continue
        
        if pair[1] in Config.config['human_name_pos']:
            keys.append(pypinyin.slug(pair[0]))
        
    return keys
    
def get_faceid_from_rawTags(raw):
    pass

###########added by yisha####################
'''
Search in db for nearby img by location
@return: sorted image dictionary by distance  
'''
def get_images_by_location(user_id, latitude, longitude, distance=1):
    image_unsort = []
    user_img = MongoHelper.get_images_by_user(user_id)
    location = user_img['location']           #update by peigang
    for img in user_img:
        abs_lat = abs(location['latitude'] - latitude)     #update by peigang
        abs_lon = abs(location['longitude'] - longitude)   #update by peigang
        if abs_lat < distance & abs_lon < distance:
            temp = ((abs_lat + abs_lon), img)
            image_unsort.append(temp)
    image_sort = sorted(image_unsort, key=lambda img: img[0])
    return image_sort[1]            #update by peigang

'''
Search in db for img with input tags
@return: sorted image dictionary by tags, ordered by time
'''
##added by peigang
def get_images_by_location_from_photos(latitude, longitude,certain_photo):
    image_unsort = []
    user_img = certain_photo
    for img in user_img:
        abs_lat = abs(img['lat'] - latitude)
        abs_lon = abs(img['lon'] - longitude)
        if abs_lat < 1 & abs_lon < 1:
            temp = ((abs_lat + abs_lon), img)
            image_unsort.append(temp)
    image_sort = sorted(image_unsort, key=lambda img: img[0])
    return image_sort[1]                               
##added by peigang

# def get_images_by_tag(user_id, input_tags):
#     image_unsort = []
#     tags = set(input_tags)
#     user_img = MongoHelper.get_images_by_user(user_id)
#     for img in user_img:
#         user_tags = set(user_img['tags'])
#         if tags.issubset(user_tags):
#             image_unsort.append(img)
#     image_sort = sorted(image_unsort, key=lambda img: img[6], reversed=True)   #time object at 6 index in image dictionary
#     return image_sort
    


##added by peigang##
def get_image_depend_timerange(raw_image,time_range):
    image_unsort = []
    user_img = raw_image
    for img in user_img:
        for item in time_range:
            if img['time'] < item[1] and img['time'] > item[0]:
                image_unsort.append(img)
    return image_unsort 
    
##0827##
def get_images_by_tag(user_id, input_tags,t):
    image_unsort = []
    image_final = []
    search_tags = list(set(input_tags))
    user_img = MongoHelper.get_images_by_user(user_id)
    print('user_img:',user_img)
    for img in user_img:
        pattern_tags = list(set(img['tags']))
        count = fuzz.ratio(search_tags, pattern_tags)
        image_unsort.append((img,count))   
    image_sort = sorted(image_unsort,key = lambda x:x[1],reverse= True)
    print('image_sort:',image_sort)         
    if t == 1:
        n = -1
        for i in range(len(image_sort)):
            j = i-1
            if i == 0 or image_sort[i][1] != image_sort[j][1]:
                n += 1
                item = []
                item.append(image_sort[i][0])
                image_final.append(item)
                print('image_final:',image_final)
            else:
                image_final[n].append(image_sort[i][0])
        return image_final
    elif t == 0:
        for item in image_unsort:
            image_final.append(item[0]['image_name'])
        return image_final

##0831##
def get_images_by_tag_from_Timage(user_id,input_tags,Timage,t):
    image_unsort = []
    image_final = [[]]
    search_tags = list(set(input_tags))
    user_img = MongoHelper.get_images_by_user_and_imagename(user_id,Timage)
    for img in user_img:
        pattern_tags = list(set(img['tags']))
        count = fuzz.ratio(search_tags, pattern_tags)
        image_unsort.append((img,count))
    image_sort = sorted(image_unsort,key = lambda x:x[1],reverse= True)         
    if t == 1:
        n = -1
        for i in range(len(image_sort)):
            j = i-1
            if i == 0 or image_sort[i][1] != image_sort[j][1]:
                n += 1
                item = []
                item.append(image_sort[i][0])
                image_final.append(item)
                print('image_final:',image_final)
            else:
                image_final[n].append(image_sort[i][0])
        return image_final
    elif t == 0:
        for item in image_unsort:
            image_final.append(item[0]['image_name'])
        return image_final


    

#0831 yisa
#0901 searchutils


def sort_by_location(latitude, longitude, image_list):
    sorted_images = []
    if not image_list:
        return None
    
    for images in image_list:
        index_images = [[],[]]
        for image in images:
            x = image['location']['longitude']
            y = image['location']['latitude']
            index_images[0].append([x, y])
            index_images[1].append(image['image_name'])
# index_images = [[[14.32, 15.32], [0.89, 0.56], [6.36, 3.66]], ['img01', 'img03', 'img04']]
        res_image_list = sort_by_closest_point(index_images, longitude, latitude)
        sorted_images += res_image_list
    return sorted_images


def sort_by_closest_point(indexer, longitude, latitude):
    sorted_images = []
    if not indexer:
        return None
    if len(indexer[1]) is 1:
        return indexer[1]
    
    pts = np.array(indexer[0])
    tree = spatial.KDTree(pts)
    loc_point = np.array([longitude, latitude])
    results = tree.query(loc_point, k=len(indexer[1]))  #[[distance],[index]]
    for res_index in results[1]:
        sorted_images.append(indexer[1][res_index])
    return sorted_images

def get_image_by_time(user_id, time_list):
    filename = get_user_path(user_id) + "/" + "time_indexer.dat"
#     filename = 'time_indexer.dat'    # modify later when md5str available
    time_indexer = mc.get(user_id)
    if not time_indexer:
        if not os.path.exists(filename):
            time_indexer = {}
        else:
            with open(filename,'rb') as fp:
                time_indexer = pickle.load(fp)
    if time_indexer is None:
        return None
    
    mc.set(user_id, time_indexer)
    time_sorted_imgs = sort_image_by_time(time_indexer, time_list)
    return time_sorted_imgs

def sort_image_by_time(img_list, time_ranges):
    # time_list: [(st, et), (st, et)]
    # img_list: [[t1, t2], [img1, img2]]
    sort_img = []
    for time_range in time_ranges:
        for time in img_list[0]:
            if time > time_range[1]:
                break
            elif time > time_range[0]:
                sort_img.append(img_list[1][img_list[0].index(time)])
    return sort_img

##0901 uploadutils

def update_time_indexer(user_id, input_img_time):
    indexer = mc.get(user_id + '_time')
    filename = get_user_path(user_id) + "/" + "time_indexer.dat"
#     filename = 'time_indexer.dat'
     
    if not indexer:
        indexer = [[input_img_time['time']], [input_img_time['image_name']]]
        mc.set(user_id, indexer)
    else:    
        with open(filename,'rb') as fp:
            indexer = pickle.load(fp)
    
    # img_list: [[t1, t2], [img1, img2]]
    imgs = []
    new_indexer = [[], []]
    i = 0
    while i < len(indexer[0]):
        img = {'time': indexer[0][i], 'image_name': indexer[1][i]}
        imgs.append(img)
        i += 1
    img = {'time': input_img_time['time'], 'image_name': input_img_time['image_name']}
    imgs.append(img)
    image_sort = sorted(imgs, key=lambda img: img['time'])
    for img in image_sort:
        new_indexer[0].append(img['time'])
        new_indexer[1].append(img['image_name'])
    mc.set(user_id, new_indexer)
    
    with open(filename, 'wb') as fp:
        pickle.dump(new_indexer,fp)
        
    print(new_indexer)
    


# if __name__ == "__main__":
#     initTime = '2000-01-01 00:00:00 +0800'
#     initTime2 = '2008-01-03 00:00:00 +0800'
#     initTime3 = '2005-09-03 00:00:00 +0800'
#     myInitTime1 = datetime.strptime(initTime, '%Y-%m-%d %X %z')
#     myInitTime2 = datetime.strptime(initTime2, '%Y-%m-%d %X %z')
#     myInitTime3 = datetime.strptime(initTime3, '%Y-%m-%d %X %z')
#     l = [{'time': myInitTime1, 'name': 'img01'},
#          {'time': myInitTime2, 'name': 'img02'},
#          {'time': myInitTime3, 'name': 'img03'}]
#     new = sorted(l, key=lambda img: img['time'])
#     print(new)
#       
#     indexer = [[myInitTime1, myInitTime2], ['img01.jpg', 'img02.jpg']]
#       
# #     filename = 'time_indexer.dat'
# #     filename = get_user_path(user_id) + "/" + "time_indexer.dat"
#       
#     with open(filename,'wb') as fp:
#         pickle.dump(indexer,fp) 
#      
#     initTime = '1999-01-01 00:00:00 +0800'
#     initTime2 = '2001-01-03 00:00:00 +0800'
#     myInitTime1 = datetime.strptime(initTime, '%Y-%m-%d %X %z')
#     myInitTime2 = datetime.strptime(initTime2, '%Y-%m-%d %X %z')
#     res = get_image_by_time('001', [(myInitTime1, myInitTime2)])
#     print(res) 

#     print(translate_tags([u'小猫']))
#     get_closest_points('wang', [0,0])
#     pair = '测试'
#     pair = ['测试','北京市','海淀区']
#     print(pypinyin.slug(pair))
#     print(pypinyin.slug((u'测试test')))
#     image = {'tags': ['a','b'], 'image_name':'y.jpg'}
#     update_user_photo_indexer('xxx', image)
#     print get_user_photo_indexer('xxx')
#Encoding=UTF8

import Config
from hashlib import md5
import os
import MongoHelper
import pickle
import pypinyin
import bmemcached
from scipy import spatial
import numpy as np
import json
import aiohttp
import http.client
from fuzzywuzzy import fuzz
from datetime import datetime
import Logger
from itertools import combinations
import time
import bisect

mc = bmemcached.Client((Config.config['memcached_host'],))

def get_similar_tags(user_id,tag_list):
    filename = get_user_path(user_id) + "/" + "image_indexer.dat"
    tag_img = mc.get(user_id + "_image")
    if not tag_img:
        if not os.path.exists(filename):
            tag_img = [[],[]]
        else:
            with open(filename,'rb') as fp:
                tag_img = pickle.load(fp)
#         mc.set(user_id + "_image", tag_img)  
          
    if tag_img is None:
        return None
    
    Logger.debug('indexer keys: ' + str(tag_img[0]))
    tag_final1 = []
    tag_final2 = [] 
    for i in tag_list:
        tag_unsort = []
        for j in tag_img[0]:
            count = fuzz.ratio(i, j)
            if count >= 80:
                tag_unsort.append((j,count))
        tag_sort = sorted(tag_unsort,key = lambda x:x[1],reverse= True)
        for item in tag_sort:
            tag_final1.append(item[0])
        if not tag_final1 in tag_final2:
            tag_final2.append(tag_final1)
    return tag_final2                  

def update_image_indexer(user_id, img):
    filename = get_user_path(user_id) + "/" + "image_indexer.dat"
    indexer = mc.get(user_id + "_image")
    if not indexer:
        if not os.path.exists(filename):
            indexer = {}
        else:
            with open(filename,'rb') as fp:
                indexer = pickle.load(fp)
    
    if indexer is None:
        return
    
    for tag in img['tags']:
        if indexer[0].count(tag) is 0:
            indexer[0].append(tag)
            indexer[1].append([img['image_name']])
        else:
            tag_index = indexer[0].index(tag)
            indexer[1][tag_index].append(img['image_name'])
    
    with open(filename,'wb') as fp:
        pickle.dump(indexer,fp)
    
    mc.set(user_id + "_image", indexer)
    Logger.debug('image indexer updated: ' + str(indexer))

def get_user_path(userId):
    md5ins = md5()
    md5ins.update(userId.encode())
    md5str = md5ins.hexdigest()
    path = Config.config['photo_root'] + md5str[0:2] + "/" + md5str[2:4] + "/" + md5str[4:6] + "/" + userId
    if not os.path.exists(path):
        os.makedirs(path)
    return path
    
def generate_access_token(userId):
    md5ins = md5()
    md5ins.update(userId.encode())
    md5ins.update(Config.config['access_token'].encode())
    return md5ins.hexdigest()

def get_images_by_tags_array(user_id, tags_list):
    Logger.debug('get_images_by_tags_array: ' + str(tags_list))
    image_res = []
    for tags in tags_list:
        img_list = get_image_by_tags(user_id, tags)
        image_res.append(set(img_list))
    
    Logger.debug('get_images_by_tags_array set list: ' + str(image_res))
    #[[set(), set()...]]
    inter_sec = []
    if len(image_res) > 1:
        for i in range(1, len(image_res) + 1):
            inter = []
            for i in combinations(image_res, i):
                res = set.intersection(*i)
                inter.append(res)
                
            inter_sec.append(inter)
    else:
        inter_sec = [image_res]
    
    final_list = []
    inter_sec.reverse()
    for i in inter_sec:
        for s in i:
            for t in s:
                if not t in final_list:
                    final_list.append(t)
            
    return final_list
    

def get_image_by_tags(user_id, tags):
    list = []
    indexer = get_image_indexer(user_id)
    for tag in tags:
        if indexer[0].count(tag) > 0:
            items = indexer[1][indexer[0].index(tag)]
            for item in items:
                if not item in list:
                    list.append(item)
            
    return list


def get_image_indexer(user_id):
    filename = get_user_path(user_id) + "/" + "image_indexer.dat"
    tag_img = mc.get(user_id + "_image")
    if not tag_img:
        if not os.path.exists(filename):
            tag_img = [[],[]]
        else:
            with open(filename,'rb') as fp:
                tag_img = pickle.load(fp)
        mc.set(user_id + "_image", tag_img)  
          
    if tag_img is None:
        return None

    return tag_img

    
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
        
    mc.set(user_id + "_location", indexer)
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
    Logger.debug('translate_tags in')
    cv_tags = mc.get('cv_tags')
    if not cv_tags:
        Logger.debug('translate_tags load from file')
        cv_tags = load_cv_tags()
        mc.set('cv_tags', cv_tags)
    
    Logger.debug('translate_tags 3')
    ret = []
    pytags = [pypinyin.slug(w) for w in tags]
    for tag in pytags:
        cand = cv_tags.get(tag, [])
        ret.extend(cand)
        
    return ret

def create_face_group(user_id):
#     host = 'https://api.projectoxford.ai/asia/face/v0'
    res = False
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': Config.config['face_api_key'],
    }
    
    body = {'name': user_id.lower()}
    
    try:
        conn = http.client.HTTPSConnection("api.projectoxford.ai")
        conn.request("PUT", "/asia/face/v0/facegroups/%s" % user_id.lower(), body=json.dumps(body), headers=headers)
        response = conn.getresponse()
        data = response.read()
        res = response.status == 200
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    finally:
        return res
    
def load_cv_tags():
    cv_tags = {}
    path = os.path.dirname(os.path.realpath(__file__)) + "/category.txt"
    if not os.path.exists(path):
        return {}
    
    file = open(path, encoding="utf-8")
    for line in file:
        items = line.strip().split(':')
        tag = items[0]
        words = [pypinyin.slug(w) for w in items[1].split('-')]
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
def get_images_by_tag(user_id, input_tags):
    Logger.debug('get_images_by_tag: ' + str(input_tags))
    tags_list = get_similar_tags(user_id, input_tags)
    Logger.debug('get_images_by_tag similar: ' + str(tags_list))
    if not tags_list:
        return []
    else:
        return get_images_by_tags_array(user_id, tags_list)

##0831##
def get_images_by_tag_from_Timage(user_id,input_tags,Timage):
    result = []
    image_names = get_images_by_tag(user_id,input_tags)
    for img in image_names:
        if (img in Timage) and (not img in result):
            result.append(img)
            
    return result
    
def update_facename_in_person_list(face_name):
    pass

##added 0831 yisa# 
def sort_by_location(user_id, latitude, longitude):    
    filename = get_user_path(user_id) + "/" + "location_indexer.dat"
    loc_indexer = mc.get(user_id + "_location")
    if not loc_indexer:
        if not os.path.exists(filename):
            loc_indexer = [[], []]
        else:
            with open(filename,'rb') as fp:
                loc_indexer = pickle.load(fp)
        mc.set(user_id + "_location", loc_indexer)
         
    if loc_indexer is None:
        return None
    
# index_images = [[[14.32, 15.32], [0.89, 0.56], [6.36, 3.66]], ['img01', 'img03', 'img04']]
    return sort_by_closest_point(loc_indexer, longitude, latitude)


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
    time_indexer = mc.get(user_id + "_time")
    if not time_indexer:
        if not os.path.exists(filename):
            time_indexer = []
        else:
            with open(filename,'rb') as fp:
                time_indexer = pickle.load(fp)
        mc.set(user_id + "_time", time_indexer)
         
    if time_indexer is None:
        return None

    time_sorted_imgs = sort_image_by_time(time_indexer, time_list)
    return time_sorted_imgs

def sort_image_by_time(img_list, time_ranges):
    # time_list: [(st, et), (st, et)]
    # img_list: [[t1, t2], [img1, img2]]
    Logger.debug('img_list:' + str(img_list))
    Logger.debug('time_ranges' + str(time_ranges))
    sort_img = []
    for time_range in time_ranges:
        for time in img_list[0]:
            if time > time_range[1]:
                break
            elif time >= time_range[0]:
                sort_img.append(img_list[1][img_list[0].index(time)])
    Logger.debug('sorted img list: ')
    Logger.debug(sort_img)
    return sort_img
    
def update_time_indexer(user_id, input_img_time):
    indexer = [[], []]
    filename = get_user_path(user_id) + "/" + "time_indexer.dat"
     
    if not os.path.exists(filename):
        indexer = [[input_img_time['time']], [input_img_time['image_name']]]
    else:
        with open(filename,'rb') as fp:
            indexer = pickle.load(fp)
            
    indexer[1].insert(bisect.bisect(indexer[0], input_img_time['time']), input_img_time['image_name'])
    bisect.insort(indexer[0], input_img_time['time']) 
    Logger.debug('update_time_indexer new indexer: ' + str(indexer))
    if indexer is None:
        return
    # img_list: [[t1, t2], [img1, img2]]
    indexer[1].insert(bisect.bisect(indexer[0], input_img_time['time']), input_img_time['image_name'])
    bisect.insort(indexer[0], input_img_time['time'])
    
    with open(filename, 'wb') as fp:
        pickle.dump(indexer,fp)
        
    mc.set(user_id + "_time", indexer)
    Logger.debug('time indexer updated:' + str(indexer))

#0831 yisa

if __name__ == "__main__":
    update_time_indexer('127f46fc-f21e-4911-a734-be4abfa8b318', {'image_name': 'img1', 'time': datetime(2014, 1, 9, 9, 5, 55, 11700)})
#     create_face_group('wang')
#     print(pypinyin.slug((u'测试test')))
#     image = {'tags': ['a','b'], 'image_name':'y.jpg'}
#     update_user_photo_indexer('xxx', image)
#     print get_user_photo_indexer('xxx')

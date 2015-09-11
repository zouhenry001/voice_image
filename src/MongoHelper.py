#Encoding=UTF8

import pymongo
import Config
from datetime import datetime


conn = pymongo.MongoClient(Config.config['mongo_url'])

def get_user(userId, password):
    db = conn.VoiceImageDB
    coll = db.user_profile
    return coll.find_one({'user_id': userId, 'password': password})

def get_user_by_id(userId):
    db = conn.VoiceImageDB
    coll = db.user_profile
    rec = coll.find_one({'user_id': userId})
    return rec;


def update_user_token(userId, newToken):
    db = conn.VoiceImageDB
    coll = db.user_profile
    doc = coll.find_one({'user_id': userId})
    if doc is not None:
        doc['token'] = newToken
        coll.save(doc)

def register_user(user):
    db = conn.VoiceImageDB
    coll = db.user_profile
    coll.insert_one(user)

def allocate_user_server():
    db = conn.VoiceImageDB
    coll = db.server_usage
    docs = coll.find()
    if docs.count() is 0:
        servers = Config.config['servers']
        for server in servers:
            server['count'] = 0
            coll.insert_one(server)
        return servers[0]['name']
    for doc in docs:
        if doc['count'] < doc['capacity']:
            return doc['name']
    return None

def increase_server_usage(server_name, num):
    db = conn.VoiceImageDB
    coll = db.server_usage
    doc = coll.find({'name': server_name})
    if doc.count() is not 0:
        newCount = num + doc[0]['count']
        serverID = doc[0]['_id']
        coll.update_one({'_id': serverID}, {'$set': {'count': newCount}})
        
def save_image(image):
    db = conn.VoiceImageDB
    coll = db.voice_images
    coll.save(image)
    
def get_unprocessed(num):
    images = []
    db = conn.VoiceImageDB
    coll = db.voice_images
    unpro = coll.find({'processed': False})
    for doc in unpro:
        images.append(doc)
    
    return images

def save_person(person):
    db = conn.VoiceImageDB
    coll = db.user_facename
    coll.save(person)

###added by peigang####0826
def extend_tags_in_existimage(user_id,image_name,tags):
    db = conn.VoiceImageDB
    coll = db.voice_images
    doc = coll.find_one({'user_id': user_id,'image_name':image_name})
    doc['tags'].extend(tags)
    coll.save(doc)
    
##0906    
def update_image_desc_and_status(desc,userId,image_name):
    db = conn.VoiceImageDB
    coll = db.voice_images
    doc = coll.find_one({'user_id': userId,'image_name':image_name})
    doc['desc'].append(desc)
    doc['processed'] = False
    coll.save(doc)
    
def get_images_by_user(user_id):
    images = []
    db = conn.VoiceImageDB
    coll = db.voice_images
    user_img = coll.find({'user_id':user_id})
    for img in user_img:
        images.append(img)
    return images
    
##added 0831
def get_images_by_user_and_imagename(user_id,Timage):
    images = []
    db = conn.VoiceImageDB
    coll = db.voice_images
    user_img = coll.find({ '$and':
                         [{'user_id': user_id},
                          {'image_name':
                           {"$in":Timage}}]
                        })
    for img in user_img:
        images.append(img)
    return images    
    
    
def get_person_id(user_id, name):
    person_ids = set()
    db = conn.VoiceImageDB
    coll = db.person_list
    unpro = coll.find({'user_id': user_id, 'name': name})
    for doc in unpro:
        person_ids.add(doc['face_id'])
    
    return person_ids
    
def get_similar_persons(user_id, persons):
    person_ids = set()
    for p in persons:
        person_ids |= get_person_id(user_id, p)
    
    similars = get_similar_candidates_rec(user_id, person_ids)
    return person_ids | similars
    
def get_similar_candidates(user_id, person_id):
    similars = set()
    db = conn.VoiceImageDB
    coll = db.person_list
    unpro = coll.find({'user_id': user_id})
    for doc in unpro:
        candidates = doc['candidates']
        if not candidates:
            continue
        
        candi = [i['faceId'] for i in candidates]
        if person_id in candi:
            similars.add(doc['face_id'])

    return similars
    
def get_similar_candidates_rec(user_id, person_ids):
    similars = list(person_ids)
    index = 0
    
    while index < len(similars):
        person_id = similars[index]
        simi = get_similar_candidates(user_id, person_id)
        for si in simi:
            if not si in similars:
                similars.append(si)
                
        index = index + 1

    return set(similars)

#0831
def update_facename_in_person_list(userId,image_name,face_name):
    db = conn.VoiceImageDB
    coll = db.voice_images
    user_image = coll.find({'user_id':userId,'image_name':image_name})
    add_facename(user_image,face_name)
    
    
def add_facename(image,face_name):
    db = conn.VoiceImageDB
    coll = db.person_list
    person = coll.find({'face_id':image['face_id']})
    person['name'].extend(face_name)
    coll.save(person)
    
#0831    
###########added by yisha####################
def check_img_exist(user_id, input_img):
    images = get_images_by_user(user_id)
    for image in images:
        if input_img is image['image_name']:
            return True
    return False

'''
Get earliest date for NLP time converter
@return: datetime object
'''
# def get_earliest_date(user_id):
#     db = conn.VoiceImageDB
#     coll = db.voice_images
#     print(coll.find({'user_id':user_id}))
#     img = coll.find({'user_id':user_id}).sort({'time': 1})
#       # sort img by ascending date
#     return img[0]['time']

def get_earliest_date(user_id):
    if user_id is not None:
        db = conn.VoiceImageDB
        coll = db.voice_images
        imgs = coll.find({'user_id':user_id})
        imgs_unsort = []
        for img in imgs:
            imgs_unsort.append(img['time'])
        imgs_sort = sorted(imgs_unsort)  # sort img by ascending date
        return imgs_sort[0]
    else:
        return datetime(2014, 1, 1, 9, 30, 17, 171000) 
    
    
def get_person(user_id, face_id):
    db = conn.VoiceImageDB
    coll = db.person_list
    coll.create_index('user_id')
    coll.create_index('face_id')
    face = coll.find_one({'user_id': user_id, 'face_id': face_id})
    return face


if __name__ == "__main__":
#     print(get_similee_candidates_rec('wang', ['94c3aa36-90ba-47a0-af6c-c67fc2863be9']))
#     print(get_similar_candidates_rec('wang', ['94c3aa36-90ba-47a0-af6c-c67fc2863be9']))
#     print(get_similar_persons('wang', [u'郭德纲']))
    print(allocate_user_server())
    increase_server_usage('localhost', 1)
    
    
    
    
    

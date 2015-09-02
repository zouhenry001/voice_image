#Encoding=UTF8

import pymongo
import Config

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
###added by peigang###
def update_user_token(userId,newToken):
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
    
# def get_server_users():
#     db = conn.VoiceImageDB
#     coll = db.server_usage
#     doc = coll.find_one()
#     if doc is None:
#         servers = Config.config['servers']
#         doc = {}
#         for server in servers:
#             doc[server['name']] = 0
#         coll.insert_one(doc)
#         
#     return doc
##yisa
def allocate_user_server():
    db = conn.VoiceImageDB
    coll = db.server_usage
    docs = coll.find()
    if docs is None:
        servers = Config.config['servers']
        for server in servers:
            server['count'] = 0
            coll.insert_one(server)
        return servers[0]['name']
    for doc in docs:
        if doc['count'] < doc['capacity']:
            return doc['name']
    return None

def increase_server_usage(server_name, count):
    db = conn.VoiceImageDB
    coll = db.server_usage
    doc = coll.find_one({'name':server_name})
    if doc is not None:
        doc['count'] += count
        coll.save(doc)
        
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

###########added by yisha####################
#search in db for img of input user_id
def get_images_by_user(user_id):
    images = []
    db = conn.VoiceImageDB
    coll = db.voice_images
    user_img = coll.find({'user_id':user_id})
    print(user_img)
    for img in user_img:
        images.append(img)
    return images

##added 0831
def get_images_by_user_and_imagename(user_id,Timage):
    images = []
    db = conn.VoiceImageDB
    coll = db.voice_images
    user_img = coll.find({'user_id':user_id,'image_name':{"$in":Timage}})
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
    
def update_person_list(user_Id,face_name):
    pass

# def get_faceid_by_face_name(user_id,face_name):
#     db = conn.VoiceImageDB
#     coll = db.person_list
#     person = coll.find({'user_id':user_id,'face_name':face_name})
#     face_id = person['face_id']
#     return face_id
    
#0831
###########added by yisha####################
# check whether img exist
def check_img_exist(user_id, input_img):
    db = conn.VoiceImageDB
    coll = db.voice_images
    images = coll.find({'user_id':user_id})
    for image in images:
        if input_img is image['image_name']:
            return True
    return False

def get_earliest_date(user_id):
    db = conn.VoiceImageDB
    coll = db.voice_images
    img = coll.find({'user_id':user_id}).sort({'time': 1})  # sort img by ascending date
    return img[0]['time']


if __name__ == "__main__":
#     print(get_similee_candidates_rec('wang', ['94c3aa36-90ba-47a0-af6c-c67fc2863be9']))
#     print(get_similar_candidates_rec('wang', ['94c3aa36-90ba-47a0-af6c-c67fc2863be9']))
    print(get_similar_persons('wang', [u'郭德纲']))
    
    
    
    

'''
Created on Sep 7, 2015

@author: v-shayi
'''
import pickle
import pymongo
import os.path
import Config
import Utils
import bmemcached

mc = bmemcached.Client((Config.config['memcached_host'],))

if __name__ == '__main__':
    user_id = '127f46fc-f21e-4911-a734-be4abfa8b318' #modify later for specific user
    conn = pymongo.MongoClient(Config.config['mongo_url'])
    db = conn.VoiceImageDB
    coll = db.voice_images
    docs = coll.find()
    
    time_indexer = [[], []]
    imgs = []
    
    for doc in docs:
        imgs.append(doc)
        
    sorted_time_indexer = sorted(imgs, key=lambda img: img['time'])
    
    for time_index in sorted_time_indexer:
        time_indexer[0].append(time_index['time'])
        time_indexer[1].append(time_index['image_name'])
        
    filename = Utils.get_user_path(user_id) + "/" + "time_indexer.dat"
    if os.path.isfile(filename):
        os.remove(filename)
     
    with open(filename,'wb') as fp:
        pickle.dump(time_indexer,fp)
    fp.close()
         
    with open(filename,'rb') as fp:
            time_indexer_read = pickle.load(fp)
    
    mc.set(user_id + "_time", time_indexer_read)
    fp.close()
    
    print(time_indexer_read[0])
    print(time_indexer_read[1])
    print(len(time_indexer_read[1]))
    
    ##################################### IMG INDEX ###########
    img_indexer = [[], []]
    docs = coll.find()
    for doc in docs:
        for tag in doc['tags']:
            if img_indexer[0].count(tag) is 0:
                img_indexer[0].append(tag)
                img_indexer[1].append([doc['image_name']])
            else:
                tag_index = img_indexer[0].index(tag)
                img_indexer[1][tag_index].append(doc['image_name'])
        
    filename = Utils.get_user_path(user_id) + "/" + "image_indexer.dat"
    if os.path.isfile(filename):
        os.remove(filename)
     
    with open(filename,'wb') as fp:
        pickle.dump(img_indexer,fp)
    fp.close()
         
    with open(filename,'rb') as fp:
            img_indexer_read = pickle.load(fp)
    
    mc.set(user_id + "_image", img_indexer_read)
    fp.close()
    
    print_index = 0
    print(img_indexer_read)
    for index_tag in img_indexer_read[0]:
        print(index_tag + ":" + str(img_indexer_read[1][print_index]))
        print_index += 1

####################### LOCATION INDEX #############################
    loc_indexer = [[], []]
    docs = coll.find()
    for doc in docs:
        loc_indexer[0].append([doc['location']['longitude'], doc['location']['latitude']])
        loc_indexer[1].append(doc['image_name'])
        
    filename = Utils.get_user_path(user_id) + "/" + "location_indexer.dat"
    if os.path.isfile(filename):
        os.remove(filename)
     
    with open(filename,'wb') as fp:
        pickle.dump(loc_indexer,fp)
    fp.close()
         
    with open(filename,'rb') as fp:
            loc_indexer_read = pickle.load(fp)
    
    mc.set(user_id + "_location", loc_indexer_read)
    fp.close()

    print(loc_indexer_read)
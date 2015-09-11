#Encoding=UTF8

config = {
    'access_token': 'secret',
    'mongo_url':'mongodb://localhost:27017/',
    'photo_root': 'D:/data/photos/',
    'servers': [{'name' : 'localhost', 'capacity': 100,'count': 0}],      #updated
    'image_process_batch': 10,
    'meaningful_pos':['ns','n','ni','nl','nz','nh','r'],
    'human_name_pos':['nh','r'],
    'object_pos':['n'],
    'memcached_host': 'localhost:11211',
    'face_api_key':'4e2bee77f4e74a5a89f725c44637b485',
    'supported_cv_tags': ['cat', 'dog', 'bird', 'fish','computer']
}

#Encoding=UTF8

config = {
    'access_token': 'secret',
    'mongo_url':'mongodb://localhost:27017/',
    'photo_root': 'D:/data/photos/',
    'servers': [{'name' : 'localhost', 'capacity': 100,'count':0}],    #updated
    'image_process_batch': 10,
    'meaningful_pos':['ns','ni','nl','nz','nt','nh'],     #updated
    'human_name_pos':['nh','r'],     #updated
    'object_pos':['n'],
    'memcached_host': '127.0.0.1',
    'face_api_key':'842282b7109d49b1914b0541cb6b1ad5'
}

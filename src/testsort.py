'''
Created on Aug 27, 2015

@author: v-pezou
'''
import Config
from hashlib import md5
import os
import MongoHelper
import pickle
import pypinyin
from pymemcache.client.base import Client
from scipy import spatial
import numpy as np
import re
import json

mc = Client((Config.config['memcached_host'], 11211))


a = [({'b':2},3),({'c':2},10),({'d':2},8)]

print(sorted(a,key=lambda x:x[1],reverse= True))

c = {1,2,3,4,5}
d = {3,4,5,6,7,8}

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

if __name__ == "__main__":
    print(translate_tags([u'小猫']))
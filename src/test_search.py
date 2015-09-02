'''
Created on Aug 28, 2015

@author: v-pezou
'''

import MongoHelper
import json
import Utils
import BaseAuthenticateHandler



user_id = 1
            # 我_r 想_v 找_v 去年_nt 夏天_nt 在_p 西雅图_ns 农贸市场_n 的_u 照片_n

meaningful = ['meiguoi','tnongmaoshichangooo']
raw_image  = Utils.get_images_by_tag(user_id, meaningful,1)   ##需修改这个函数：search时容错、关联度
            
print(raw_image)         




print(float(" 3.015"))






































if __name__ == '__main__':
    pass
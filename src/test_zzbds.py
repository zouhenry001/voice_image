'''
Created on Aug 27, 2015

@author: v-pezou
'''
import re
from fuzzywuzzy import fuzz

line = "tttiananmenjj";

# matchObj = re.match( r'dogs', line, re.M|re.I)
# if matchObj:
#    print("match --> matchObj.group() : ", matchObj.group())
# else:
#    print("No match!!")

matchObj = re.search( r'(tiananmen)', line, re.M|re.I)
if matchObj:
   print("search --> matchObj.group() : ", matchObj.group())
else:
   print("No match!!")
   
pair1 = ["this is a test","ni ma bi",'llllllllltttl']
pair2 = ["this is a test!","ni ma bi",'llllllllll','fgfgfgfg'] 
print(fuzz.ratio(pair1, pair2))
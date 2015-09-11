#Encoding=UTF8

import re
import datetime
import calendar
from pymemcache.client.base import Client 
import os
import pickle
import Logger
import Lunardate
import MongoHelper

############ abs
# 2014年_nt 的_u 照片_n
# 3月份_nt
# 2014年_nt 3月_nt 的_u 照片_n
# 15日_nt 的_u 照片_n
# 3月_nt 11日_nt 的_u 照片_n

############ relative
# 去年_nt 的_u 照片_n
# 春天_nt 的_u 照片_n
# 今年_nt 春天_nt 的_u 照片_n
# 上个月_nt 的_u 照片_n
# 最近_nt 的_u 照片_n
# 上周_nt 的_u 照片_n
# 今天_nt 的_u 照片_n
# 昨天_nt 的_u 照片_n
# 上周六_nt 的_u 照片_n
# 前年_nt 的_u 照片_n
result = []#最后得到的时间结果
final = []#_nd 和 _nt词性的列表
search_string = []#只含有_nt词性的列表，用于搜索具体年月日


def do_parse_raw_year(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    m = re.search(regex, date_str)
    if not m:
        return None
    
    year = int(m.group(1))
    return (year, year)

def do_parse_last_year(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    start = datetime.date.today()
    return (start.year - 1, start.year - 1)

def do_parse_this_year(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    start = datetime.date.today()
    return (start.year, start.year)

def do_parse_last2_year(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    start = datetime.date.today()
    return (start.year - 2, start.year - 2)

def do_parse_raw_month(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    m = re.search(regex, date_str)
    if not m:
        return None
    
    month = int(m.group(1))
    return (month, month)

def do_parse_last_month(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    start = datetime.date.today()
    day = start.day
    delta = datetime.timedelta(days=day + 1)
    start = start - delta
    (day1, ndays) = calendar.monthrange(start.year, start.month)
    return (start.year, start.month, 1, start.year, start.month, ndays)

def do_parse_spring(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (2, 5)

def do_parse_summer(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (5, 8)

def do_parse_autumn(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (8, 10)

def do_parse_winter(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (10, 12)

def do_parse_raw_day(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    m = re.search(regex, date_str)
    if not m:
        return None
    
    day = int(m.group(1))
    return (day, day)

def do_parse_recent(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    now = datetime.date.today()
    delta = datetime.timedelta(days=7)
    start = now - delta
    (day1, ndays) = calendar.monthrange(start.year, start.month)
    return (start.year, start.month, start.day, now.year, now.month, now.day)

def do_parse_n_recent(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    now = datetime.date.today()
    m = re.search(regex, date_str)
    if not m:
        return None
    
    day = m.group(2)
    if not day:
        day = 7
    else:
        day = int(day)
    delta = datetime.timedelta(days=day)
    start = now - delta
    return (start.year, start.month, start.day, now.year, now.month, now.day)

def do_parse_last_weekday(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    now = datetime.date.today()
    wd = calendar.weekday(now.year, now.month, now.day)
    m = re.search(regex, date_str)
    if not m:
        return None
    
    day = m.group(1)
    if not day:
        day = 7 + wd
        delta = datetime.timedelta(days=day)
        start = now - delta
        end = start + datetime.timedelta(days=7)
        return (start.year, start.month, start.day, end.year, end.month, end.day)
    else:
        day = 7 + wd + int(convert_chinese_num(day))
        delta = datetime.timedelta(days=day)
        start = now - delta
        return (start.year, start.month, start.day, start.year, start.month, start.day)
    

def do_parse_last_n_week(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    now = datetime.date.today()
    m = re.search(regex, date_str)
    if not m:
        return None
    
    day = m.group(1)
    if not day:
        day = 21
        delta = datetime.timedelta(days=day)
        start = now - delta
    else:
        day = 7 * int(convert_chinese_num(day))
        delta = datetime.timedelta(days=day)
        start = now - delta
        
    return (start.year, start.month, start.day, now.year, now.month, now.day)

def do_parse_today(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    start = datetime.date.today()
    return (start.year, start.month, start.day, start.year, start.month, start.day)

def do_parse_lastday(regex, date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    now = datetime.date.today()
    delta = datetime.timedelta(days=1)
    start = now - delta
    return (start.year, start.month, start.day, start.year, start.month, start.day)

def do_parse_newyears_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str) 
    return (1, 1)

def do_parse_valentine_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (2,14)

def do_parse_women_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (3,8)

def do_parse_plantree_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (3,12)

def do_parse_fools_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (4,1)

def do_parse_qingming_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (4,5)

def do_parse_labors_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (5,1)

def do_parse_children_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (6,2)

def do_parse_71_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (8,1)

def do_parse_81_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (8,1)

def do_parse_nation_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (10,1)

def do_parse_halloween_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (10,31)

def do_parse_singal_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (11,11)

def do_parse_thanksgiving_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (11,25)

def do_parse_christmasEve_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (12,24)

def do_parse_christmas_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (12,25)

def do_parse_chinesenewyear_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (1,1)#阴历

def do_parse_lantern_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (1,15)#阴历

def do_parse_dragonboat_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (5,5)#阴历

def do_parse_chinesevalentine_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (7,7)#阴历

def do_parse_midautumn_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (8,15)#阴历

def do_parse_doubleninth_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (9,9)#阴历

def do_parse_laba_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (12,8)#阴历

def do_parse_newyeareve_day(regex,date_str):
    Logger.debug('do parse: ' + regex + " - " + date_str)
    return (12,30)#阴历

#user_earliest_datetime = "2000-1-1 00:00:00 +0800"
user_earliest_datetime = None #datetime.datetime.strptime("2010-1-1 00:00:00 +0800",'%Y-%m-%d %X %z')

year_regex = [(u'(\d+)年', do_parse_raw_year),
              (u'去年', do_parse_last_year),
              (u'今年', do_parse_this_year),
              (u'前年', do_parse_last2_year),]

month_regex = [(u'(\d+)月[份]{0,1}', do_parse_raw_month),
               (u'春[天季]', do_parse_spring),
               (u'夏[天季]', do_parse_summer),
               (u'秋[天季]', do_parse_autumn),
               (u'冬[天季]', do_parse_winter)]

day_regex = [(u'(\d+)日', do_parse_raw_day)]

relative_regex = [(u'[上|(最近)]([一二三四五六七八九两1-9]{0,1})[个]{0,1}月', do_parse_last_month),
                  (u'今天', do_parse_today),
                  (u'昨天', do_parse_lastday),
                  (u'最近((\d+)天){0,1}', do_parse_n_recent),
                  (u'上周([一二三四五六日1-6]{0,1})', do_parse_last_weekday),
                  (u'[上|(最近)]([一二三四五六七八九两1-9])周', do_parse_last_n_week)]

festival_regex = [(u'((元旦节?)|(新年))', do_parse_newyears_day),
                 (u'情人节',do_parse_valentine_day),
                 (u'((三八妇女节)|(妇女节))',do_parse_women_day),
                 (u'植树节',do_parse_plantree_day),
                 (u'愚人节',do_parse_fools_day),
                 (u'清明节?',do_parse_qingming_day),
                 (u'((劳动节)|(五一))',do_parse_labors_day),
                 (u'儿童节',do_parse_children_day),
                 (u'(建党节)|(建党日)|(七一)',do_parse_71_day),
                 (u'建军节',do_parse_81_day),
                 (u'((国庆节?)|(十一))',do_parse_nation_day),
                 (u'万圣节',do_parse_halloween_day),
                 (u'((光棍节)|(双十一))',do_parse_singal_day),
                 (u'感恩节',do_parse_thanksgiving_day),
                 (u'平安夜',do_parse_christmasEve_day),
                 (u'圣诞节?',do_parse_christmas_day)]

lunar_festival_regex = [(u'(春节)|(正月初一)|(大年初一)',do_parse_chinesenewyear_day),
                        (u'(元宵节)|(灯节)|(正月十五)',do_parse_lantern_day),
                        (u'(端午节?)|(粽子节)',do_parse_dragonboat_day),
                        (u'七夕节?',do_parse_chinesevalentine_day),
                        (u'中秋节?',do_parse_midautumn_day),
                        (u'重阳节?',do_parse_doubleninth_day),
                        (u'腊八节?',do_parse_laba_day),
                        (u'除夕夜?',do_parse_newyeareve_day)]

def convert_chinese_num(num):
    if num == '1'  or num == u'一':
        return 1
    elif num == '2'  or num == u'二' or num == u'两':
        return 2
    elif num == '3'  or num == u'三':
        return 3
    elif num == '4'  or num == u'四':
        return 4
    elif num == '5'  or num == u'五':
        return 5
    elif num == '6'  or num == u'六':
        return 6
    elif num == '7'  or num == u'七':
        return 7
    elif num == '8'  or num == u'八':
        return 8
    elif num == '9'  or num == u'九':
        return 9

def trans_date_to_string(year,month,day):
    year_string = str(year)
    month_string = str(month)
    day_string = str(day)
    
    date_string = year_string + '-' + month_string + '-' + day_string + ' 00:00:00 +0800'
    return date_string

def trans_datetime_to_string(year,month,day,hour,minute,second):
    year_string = str(year)
    month_string = str(month)
    day_string = str(day)
    hour_string = str(hour)
    minute_string = str(minute)
    second_string = str(second)
    
    datetime_string = year_string + '-' + month_string + '-' + day_string + ' '+ hour_string + ':' + minute_string + ':' + second_string + ' +0800'
    return datetime_string

def parse_nl_date(date_str):   
    now = datetime.datetime.now()
    
    (start_year, start_month, start_day) = (now.year, now.month, now.day)
    (end_year, end_month, end_day) = (now.year, now.month, now.day)
    
    year_set = False
    month_set = False
    day_set = False
    festival_set = False
    islunar_set = False
            
    for st in date_str:
        #print('paring string is' + st)
        if not (re.match(u'(春节)|(正月十)|(正月初)|(大年初)|(元宵节)|(灯节)|(端午)|(粽子节)|(七夕)|(中秋)|(重阳)|(腊八)|(除夕)', st) == None):
            islunar_set = True
        res = parse_relative(st)
        #print('after parsing res is:')
        #print(res)
        if res:
            (start_year, start_month, start_day, end_year, end_month, end_day) = res
        else:
            res = parse_year(st)
            if res:
                (start_year, end_year) = res
                year_set = True
            res = parse_festival(st)
            if res:
                (start_month,start_day) = res
                (end_month,end_day)     = res
                month_set = True
                day_set = True
                festival_set =True
            res = parse_lunar_festival(st)
            if res:
                (start_month,start_day) = res
                (end_month,end_day)     = res
                month_set = True
                day_set = True
            if year_set and  month_set and day_set and festival_set:
                break 
            res = parse_month(st)
            if res:
                (start_month, end_month) = res
                month_set = True
            res = parse_day(st)
            if res:
                (start_day, end_day) = res
                day_set = True      
            if not year_set and not month_set and not day_set:
                break
            
            if not year_set:
                (start_year, end_year) = (now.year, now.year)
                
            if not month_set:
                if year_set:
                    (start_month, end_month) = (1,12)
                elif day_set:
                    (start_month, end_month) = (now.month, now.month)
                    
            if not day_set:
                (start_day, end_day) = (1,31)
                
    if islunar_set:
        lunar_start = Lunardate.LunarDate(start_year, start_month, start_day).toSolarDate()
        lunar_end = Lunardate.LunarDate(end_year, end_month, end_day).toSolarDate()
        
        start_time = datetime.datetime(lunar_start.year, lunar_start.month, lunar_start.day, 0, 0, 1, 171000)
        end_time = datetime.datetime(lunar_end.year, lunar_end.month, lunar_end.day, 23, 59, 59, 171000)  
          
        result.append((start_time,end_time))
        
        if not year_set:
            user_earliest_datetime_str = user_earliest_datetime.__str__()
            user_earliest_year = int(user_earliest_datetime_str[0:4])
            while(start_year > user_earliest_year):
                start_year = start_year - 1
                end_year = end_year - 1
                lunar_start = Lunardate.LunarDate(start_year, start_month, start_day).toSolarDate()
                lunar_end = Lunardate.LunarDate(end_year, end_month, end_day).toSolarDate()
                start_time = datetime.datetime(lunar_start.year, lunar_start.month, lunar_start.day, 0, 0, 1, 171000)
                end_time = datetime.datetime(lunar_end.year, lunar_end.month, lunar_end.day, 23, 59, 59, 171000)   
                result.append((start_time,end_time))
        
        return result
    
    start_time = datetime.datetime(start_year, start_month, start_day, 0, 0, 1, 171000)
    end_time = datetime.datetime(end_year, end_month, end_day, 23, 59, 59, 171000)
          
    result.append((start_time,end_time))
      
    if not year_set and not islunar_set:
        #用户没有说明具体哪一年 需要从最新的一年开始一直到用户最早出现的一年的时间全部都返回
        user_earliest_datetime_str = user_earliest_datetime.__str__()
        user_earliest_year = int(user_earliest_datetime_str[0:4])
        while(start_year > user_earliest_year):
            start_year = start_year - 1
            end_year = end_year - 1
            start_time = datetime.datetime(start_year, start_month, start_day, 0, 0, 1, 171000)
            end_time = datetime.datetime(end_year, end_month, end_day, 23, 59, 59, 171000)
            result.append((start_time,end_time))
    
    return result

def parse_date_item(date_str, regex):
    parse_func = None
    parse_reg = None
    for reg, func in regex:
        m = re.search(reg, date_str)
        if m:
            parse_func = func
            parse_reg = reg
            break
    
    if parse_func:
        return parse_func(parse_reg, date_str)
    
    return None

def parse_year(date_str):
    return parse_date_item(date_str, year_regex)

def parse_month(date_str):
    return parse_date_item(date_str, month_regex)

def parse_day(date_str):
    return parse_date_item(date_str, day_regex)

def parse_relative(date_str):
    return parse_date_item(date_str, relative_regex)

def parse_festival(date_str):
    return parse_date_item(date_str,festival_regex)

def parse_lunar_festival(date_str):
    return parse_date_item(date_str,lunar_festival_regex)

def time_api(str,user_id):
    search_string.clear()
    final.clear()
    result.clear()
    words = str.split(" ")
    global user_earliest_datetime
    user_earliest_datetime = MongoHelper.get_earliest_date(user_id)
    user_earliest_datetime_string = trans_datetime_to_string(user_earliest_datetime.year,user_earliest_datetime.month,user_earliest_datetime.day,user_earliest_datetime.hour,user_earliest_datetime.minute,user_earliest_datetime.second)
    user_earliest_datetime = datetime.datetime.strptime(user_earliest_datetime_string,'%Y-%m-%d %X %z')
    print(words)
    for word in words:
        if "_nt" in word:
             w = re.search(u'(\w+)_nt',word).group(1)
             final.append(w)
             search_string.append(w)
        if "_nd" in word:
             w = re.search(u'(\w+)_nd',word).group(1)
             final.append(w)
            
             sort_set = True
             break
    if(search_string == []):
        return None
    else:
         return parse_nl_date(search_string)
if __name__ == "__main__":
    # relative time
#     print parse_nl_date([u'上个月'])
#     print parse_nl_date([u'最近'])
#     print parse_nl_date([u'最近3天'])
#     print parse_nl_date([u'最近3个月'])
#     print parse_nl_date([u'上周'])
#     print parse_nl_date([u'上周五'])
#     print parse_nl_date([u'上两周'])
#     
#     #absolute time
#     print parse_nl_date([u'2014年'])
#     print parse_nl_date([u'今年'])
#     print parse_nl_date([u'去年'])
#     print parse_nl_date([u'前年'])
#     print parse_nl_date([u'3月份'])
#     print parse_nl_date([u'春天'])
#     print parse_nl_date([u'春季'])
#     print parse_nl_date([u'夏天'])
#     print parse_nl_date([u'秋天'])
#     print parse_nl_date([u'冬天'])
    
    Logger.debug(time_api( "我_r 要_v 找_v 去年_nt 端午节_nt 在_p 微软_ni 附近_nd 拍_v 的_u 照片_n",None))
    Logger.debug(time_api( "我_r 要_v 找_v 今年_nt 劳动节_nt 在_p 微软_ni 附近_nd 拍_v 的_u 照片_n",None))
    #print (Lunardate.LunarDate(1998, 9, 4).toSolarDate())
    
    
#     print parse_nl_date([u'3月'])
#     print parse_nl_date([u'15日'])
#     print parse_nl_date([u'2014年',u'3月份', u'15日'])
#     print parse_nl_date([u'2014年',u'3月份'])



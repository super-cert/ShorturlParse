#-*- coding: utf-8 -*-

import email, getpass, imaplib, os
import re
import base64
import urllib.request
import time 
import urllib.parse
import unicodedata
import csv
import exifread
import hashlib
import operator
import privacy
from gmplot import gmplot


def googlemap(gpsdictions,num):
    if(len(gpsdictions)==0): 
        print("sorry. no jpg or no exif data ")
        return 0
    print(gpsdictions)
    gmap = gmplot.GoogleMapPlotter(gpsdictions[0][1][0],gpsdictions[0][1][1], 13)

    lat = []
    lot = []
    timelabel = []

    for value in gpsdictions.values():
        lat.append(value[1][0])
        lot.append(value[1][1])
        timelabel.append(value[0])
    print("start time : " + timelabel[0])
    print("end time : " + timelabel[-1])
    gmap.plot(lat, lot, 'cornflowerblue', edge_width=5)
    n = -1
    for i, j in zip(lat,lot):
        n+=1
        gmap.marker(i,j,'red', title=timelabel[n])
    if(int(num)==1):
        gmap.draw(os.path.join(dirpath,"tracker.html"))
    elif(int(num)==2):
        gmap.draw("total_tracker.html")
       

def readexcel(num):

    if(num==1):
        re_path = dirpath

        with (open(os.path.join(re_path,'data.csv'),encoding='utf-16')) as files:
            data = csv.reader(files,delimiter=',')

            sortedlist = sorted(data, key=operator.itemgetter(0))

        print("----readexcel----")
        #print(sortedlist[0])
        #print(sortedlist[1])
        matdist = {}
        n = -1
        for row in sortedlist:
            n+=1
            matdist[n] = (str(row)[1:-1].split('\\t'))

        #location= [float(matdist[2][4][:-8]),float(matdist[2][5][:-8])]
        
        gpsdiction = {}
        j = -1
        for i in range(0, len(matdist)):
            
            if not (matdist[i][4]=='N/A'):
                j+=1
                gpsdiction[j] = matdist[i][0][1:], [float(matdist[i][4][:-8]),float(matdist[i][5][:-8])]
    if(num==2):
        with (open('total.csv',encoding='utf-16')) as files:
            data = csv.reader(files,delimiter=',')

            sortedlist = sorted(data, key=operator.itemgetter(0))

        print("----totalreadexcel----")
        #print(sortedlist[0])
        #print(sortedlist[1])
        matdist = {}
        n = -1
        for row in sortedlist:
            n+=1
            matdist[n] = (str(row)[1:-1].split('\\t'))

        gpsdiction = {}
        j = -1
        for i in range(0, len(matdist)):
            
            
            if not (matdist[i][4]=='N/A'):
                j+=1
                gpsdiction[j] = matdist[i][0][1:], [float(matdist[i][4][:-8]),float(matdist[i][5][:-8])]

    return(gpsdiction)




def _convert_to_degress(value):

    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m/60.0) + (s/3600.0)


def getGPS(filepath):
    '''
    returns gps data if present other wise returns empty dictionary
    '''
    with open(filepath, 'r') as f:
        tags = exifread.process_file(open(filepath,'rb'))
        latitude = tags.get('GPS GPSLatitude')
        latitude_ref = tags.get('GPS GPSLatitudeRef')
        longitude = tags.get('GPS GPSLongitude')
        longitude_ref = tags.get('GPS GPSLongitudeRef')
        if latitude:
            lat_value = _convert_to_degress(latitude)
            if latitude_ref.values != 'N':
                lat_value = -lat_value
        else:
            return []
        if longitude:
            lon_value = _convert_to_degress(longitude)
            if longitude_ref.values != 'E':
                lon_value = -lon_value
        else:
            return []
        return [lat_value,lon_value]
    return []


def makecsv(diction):

    with open(os.path.join(dirpath,'data.csv'), 'a', encoding='utf-16', newline='') as csvfile: #각 경로파일 

        writer = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #writer.writerow(["폴더명","파일명","좌표x","좌표y","md5","sha1"])
        
        for key in dictions.keys():
            writer.writerow(diction.get(key))
    print("----makecsv----")
    print("length : " +str(len(diction))+ " of jpg file")
    with open('total.csv', 'a', encoding='utf-16', newline='') as csvfile2: #각 경로파일 

        writer = csv.writer(csvfile2, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #writer.writerow(["폴더명","파일명","좌표x","좌표y","md5","sha1"])
        
        for key in dictions.keys():
            writer.writerow(diction.get(key))
    print("----totalmakecsv----")

def regfilter(raw_url):
    regev = '(https:\/\/hoy.kr\/\w{4,7}|http:\/\/bitly.kr\/\w{4,7}|https:\/\/bit.ly\/\w{4,7}| https:\/\/goo.gl\/\w{7})'
    test = (re.search(regev,raw_url))
    if test is None:
        return False
    else:
        return(test[0])
    
def rmdup(dictions):
    errwer=[]
    for value in dictions.values():
        
        errwer.append(value[3])
    content=[]
    for i in range(0, len(errwer)-1):
        if(errwer[i]==errwer[i+1]):
            content.append(errwer[i])
    rm = []
    for key, value in dictions.items():
        for i in content:
            if(i==value[3]):
                rm.append(key)

    for i in range(0, len(rm)-1):
        del dictions[rm[i]]

    return(dictions)

def returnurl(shorturl):
    
    try:
        response = urllib.request.urlopen(shorturl)
        if(response.getcode() == 200):

            
            raw_url =(response.geturl())
            
            if(response.read(2)[0]==int(255) and response.read(2)[1]==int(224)):
                realname =downloadfile(raw_url)
                return [shorturl,os.path.split(raw_url)[0]+'/'+realname,realname]

    except :
        pass
        
def redate(date):
    reg = '\d{1,2} \w{3,10} \d{4} \d{2}:\d{2}:\d{2}'

    test_re = re.search(reg,date)
    if(test_re is None):
        return


    test_list = list(test_re[0].split(' '))
    undertime = test_list[3].split(':')[0:2]

    if test_list[1]=='Aug':
        test_list[1]='8'

    returnvalue = "%04d-%02d-%02d %02d:%02d" % (int(test_list[2]), int(test_list[1]), int(test_list[0]), int(undertime[0]), int(undertime[1]))
    return returnvalue

def lookup():

    jpg_files = [f for f in os.listdir(downloadpath) if f.endswith('.jpg')]
    print(jpg_files)
    return jpg_files

def hashreturn(filepath):
        
    with open(filepath,'rb') as openfiles:

        md5 = (hashlib.md5(openfiles.read()).hexdigest())
        openfiles.seek(0)
        sha1 = (hashlib.sha1(openfiles.read()).hexdigest())
        return[md5,sha1]

def gpsandhash(dictions):

    for key, value in dictions.items():

        filepath = (os.path.join(dirpath,value[3]))
        xy = getGPS(filepath)
        
        if len(xy) ==0:
            xy = ["N/A","N/A"]
        dictions[key]+=xy
        hashcode= hashreturn(filepath)
        dictions[key]+=hashcode
    
    return dictions


def makedirs():
    
    
    now = time.localtime()
    nowday = "%04d-%02d-%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
    
    try:
        if not(os.path.isdir(nowday)):
            os.makedirs(os.path.join(nowday))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create Directory");
            raise
    print(nowday + " Directory making success..")
    return nowday

def downloadfile(raw_url):

    try:
        test = raw_url.split(chr(47))[-1]
        realname = unicodedata.normalize('NFC', urllib.parse.unquote((test))) ## 한글깨짐을 처리해주는 곳
        
        fullfilename = os.path.join(dirpath,realname)
        
        urllib.request.urlretrieve(raw_url, fullfilename)
        print("downloaded file : " + realname)
        return realname
    except:
        pass



def read_email_from_gmail():
    
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)   
    mail.login(FROM_EMAIL,FROM_PWD)
    mail.select('inbox')
    typedata, data = mail.search(None, '(FROM "Kyle Choi")')
    mail_ids = data[0]
    id_list = mail_ids.split()
    dictions = {}
    n=-1
    for i in reversed(id_list):
        typ, data = mail.fetch(i, '(RFC822)' )
        
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('utf-8'))
                mail_date = redate(msg['Date'])
        
                if('2018-08-11'==mail_date[:-6]): #todaydate 넣기 

                    test = str(msg.get_payload()[1])
                    testlist = []
                    testlist.append(test.split('\n'))
                    print("--------match mail----------")
                    print("mail_date : " + mail_date)
                    for j in testlist[0]:
                        #print(i)
                        raw_url=j
                        if str(raw_url) is None:
                            continue
                        
                        filtered_url =regfilter(str(raw_url))
                        if not filtered_url is None and not filtered_url is False:
                            
                            count = len(filtered_url)
                            while(count>0):
                                count-=1
                                if str(filtered_url[count-1])==chr(47):
                                    break

                                shorturl = (returnurl(filtered_url[0:count+1]))

                                if not shorturl is None:
                                    break
                            
                            n+=1
                            dictions[n] = []
                            dictions[n].append(mail_date)
                            dictions[n]+=shorturl
                            print("regfiltered into : "+filtered_url)


    return rmdup(dictions) # 딕셔너리에 저장된 데이터를 sort하고 나중에 구글맵에 찍을때 순서대로 들어가기 위해서

if __name__ == "__main__":
    
    
    ##기본세팅
    todaydate = makedirs()                  # 그날날짜의 폴더생성 (상대경로로 만들어짐)
    dirpath = todaydate+"\\"                # 폴더의 경로
    downloadpath = os.path.join("C:\\Users\\dpddpdgn\\OneDrive\\bob\\컨설팅과제\\최원영멘토님\\곧과제가옵니다\\",dirpath)
    ORG_EMAIL   = "@gmail.com"              
    FROM_EMAIL  = privacy.account + ORG_EMAIL # d
    FROM_PWD    = privacy.password
    SMTP_SERVER = "imap.gmail.com"
    SMTP_PORT   = 993
    
    ## 이메일을 실제로 읽고 작업하는 공간
    dictions = (read_email_from_gmail()) ##1. main class를 가져옴 jpg 파일 생성
    #dictions = {0: ['2018-08-05 13:50', 'https://hoy.kr/N6DB', 'http://fl0ckfl0ck.info/私は人間の屑です.jpg', '私は人間の屑です.jpg'], 1: ['2018-08-05 13:50', 'https://hoy.kr/SvCC', 'http://fl0ckfl0ck.info/뽀삐.jpg', '뽀삐.jpg']}
    dictions = gpsandhash(dictions) ##2. gps값과 해시값 추가
    ## 딕셔너리로 뽑아낸후 
    ## 이작업에서 들어가야할 칼럼은 1. date , 2. shorturl, 3.Full url, 4. 파일이름, 5. x, 6. y, 7. md5, 8.sha1
    #dictions ={0: ['2018-08-05 13:50', 'https://hoy.kr/N6DB', 'http://fl0ckfl0ck.info/私は人間の屑です.jpg', '私は人間の屑です.jpg', '0a794cc0b4902b767e87cfd83e5a400d', '74a9280c2216560db6443c9009f02630d007e33f'], 1: ['2018-08-05 13:50', 'https://hoy.kr/SvCC', 'http://fl0ckfl0ck.info/뽀삐.jpg', '뽀삐.jpg', 'c99c8714a4c619aa9fc9e5e4b39f7aad', '8fd801116f77f80acec53423b1c79dee9c13263c']}
    makecsv(dictions) ## 3. csv 생성
    #=dictions = {0: ["'2018-08-05 13:50", 'https://hoy.kr/N6DB', 'http://fl0ckfl0ck.info/私は人間の屑です.jpg', '私は人間の屑です.jpg', 'N/A', 'N/A', '0a794cc0b4902b767e87cfd83e5a400d', "74a9280c2216560db6443c9009f02630d007e33f'"], 1: ["'2018-08-05 13:50", 'https://hoy.kr/N6DB', 'http://fl0ckfl0ck.info/私は人間の屑です.jpg', '私は人間の屑です.jpg', 'N/A', 'N/A', '0a794cc0b4902b767e87cfd83e5a400d', "74a9280c2216560db6443c9009f02630d007e33f'"], 2: ["'2018-08-05 13:50", 'https://hoy.kr/SvCC', 'http://fl0ckfl0ck.info/뽀삐.jpg', '뽀삐.jpg', 'N/A', 'N/A', 'c99c8714a4c619aa9fc9e5e4b39f7aad', "8fd801116f77f80acec53423b1c79dee9c13263c'"], 3: ["'2018-08-05 13:50", 'https://hoy.kr/SvCC', 'http://fl0ckfl0ck.info/뽀삐.jpg', '뽀삐.jpg', 'N/A', 'N/A', 'c99c8714a4c619aa9fc9e5e4b39f7aad', "8fd801116f77f80acec53423b1c79dee9c13263c'"]}
    print(dictions)
    gpsdictions = readexcel(1) ## 4.각자의 엑셀읽기 
    googlemap(gpsdictions,1) ## 5. 구글 찍기
    exit(-1)
    gpsdictions = readexcel(2) ## 4.전체 엑셀읽기 
    googlemap(gpsdictions,2) ## 5. 구글 찍기

    
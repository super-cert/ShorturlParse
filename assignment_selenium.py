from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import privacy 
import re
import email, getpass, imaplib, os
import base64
import urllib.request
import time 
import urllib.parse
import unicodedata
import csv
import exifread
import hashlib
import operator
from gmplot import gmplot

def googlemap(gpsdictions,num):
    if(len(gpsdictions)==0): 
        print("sorry. no jpg or no exif data ")
        return 0
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

def selenium_detail_date(raw_detail_date):
    fil_detail_date_str = re.findall(r'\d{1,}',raw_detail_date)

    fil_detail_date = "%04d-%02d-%02d %02d:%02d" %(int(fil_detail_date_str[0]),int(fil_detail_date_str[1]),int(fil_detail_date_str[2]),int(fil_detail_date_str[3]),int(fil_detail_date_str[4]))
    return(fil_detail_date)

def selenium_date(raw_date):
    

    fil_str = re.findall(r'\d{1,}', raw_date)

    fil_date = "2018-%02d-%02d" % (int(fil_str[0]), int(fil_str[1]))
    return(fil_date)

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
        realname = unicodedata.normalize('NFC', urllib.parse.unquote((test)))
        
        fullfilename = os.path.join(dirpath,realname)
        
        urllib.request.urlretrieve(raw_url, fullfilename)
        print("downloaded file : " + realname)
        return realname
    except:
        pass

def returnurl(shorturl):
    
    
    try:
        response = urllib.request.urlopen(shorturl)
        if(response.getcode() == 200):
            
            raw_url =(response.geturl())

            if(response.read(2)[0]==int(255) and response.read(2)[1]==int(224)):
                realname =downloadfile(raw_url)
                print("ok")
            #print(os.path.split(raw_url)[:-1])
                return [shorturl,os.path.split(raw_url)[0]+'/'+realname,realname]

    except :
        
        pass
 
def regfilter(raw_url):
    regev = '(https:\/\/hoy.kr\/\w{4,7}|http:\/\/bitly.kr\/\w{4,7}|https:\/\/bit.ly\/\w{4,7}| https:\/\/goo.gl\/\w{7})'
    test = (re.search(regev,raw_url))
    if test is None:
        return False
    else:

        print(test[0])
        return(test[0])

def selenium_read_email():

    driver = webdriver.Chrome('C:\\Users\\dpddpdgn\\Downloads\\chromedriver_win32\\chromedriver')
    driver.implicitly_wait(3)
    baseurl = 'http://mail.google.com/mail/h/'
    emailurl= 'https://mail.google.com/mail/u/0/#inbox'
    driver.get(baseurl) #드라이버 선언    
    driver.find_element_by_id("identifierId").send_keys(privacy.account)
    driver.find_element_by_id("identifierNext").click()
    driver.find_element_by_name("password").send_keys(privacy.password)
    driver.find_element_by_id("passwordNext").click()
    driver.implicitly_wait(3)
    xpath_sender = '/html/body/table[2]/tbody/tr/td[2]/table[1]/tbody/tr/td[2]/form/table[2]/tbody/tr[{}]/td[2]'   # 메일 송신자 
    xpath_date = '/html/body/table[2]/tbody/tr/td[2]/table[1]/tbody/tr/td[2]/form/table[2]/tbody/tr[{}]/td[4]'     # 날짜 부분
    xpath_body = '/html/body/table[2]/tbody/tr/td[2]/table[1]/tbody/tr/td[2]/form/table[2]/tbody/tr[{}]/td[3]/a/span/font[2]' #텍스트부분
    getinto_detail = '/html/body/table[2]/tbody/tr/td[2]/table[1]/tbody/tr/td[2]/form/table[2]/tbody/tr[{}]/td[3]'  # 각 메일로 들어가는 부분
    date_detail = '/html/body/table[2]/tbody/tr/td[2]/table[1]/tbody/tr/td[2]/table[4]/tbody/tr/td/table[1]/tbody/tr[1]/td[2]'  #구체적인 날짜 부분
    mail_count_text = '/html/body/table[2]/tbody/tr/td[2]/table[1]/tbody/tr/td[2]/form/table[1]/tbody/tr/td[2]/b[3]' #메일 전체 갯수를 가지고 있는 속성
    mail_count = int(driver.find_element_by_xpath(mail_count_text).text)
    dictions = {}
    n=-1
    for i in range(mail_count,0,-1): #메일 카운트만큼 
            if driver.find_element_by_xpath(xpath_sender.format(i)).text == 'Kyle Choi':
                shortdate = selenium_date(driver.find_element_by_xpath(xpath_date.format(i)).text)
                if shortdate == '2018-08-11': #당일 날짜 #todaydate
                    mail_body = driver.find_element_by_xpath(xpath_body.format(i)).text #메일본문읽고
                    driver.find_element_by_xpath(getinto_detail.format(i)).click() #날짜를 읽기 위해 접속하고 
                    detaildate = selenium_detail_date((driver.find_element_by_xpath(date_detail).text))
                    driver.execute_script("window.history.go(-1)")  #뒤로 가기 
                    first_reg = (regfilter(mail_body[2:]))
                    
                    if not first_reg is None and not first_reg is False:
                        
                        count = len(first_reg)
                    
                        while(count>0):
                            count-=1
                            if str(first_reg[count-1])==chr(47):
                                print("done : "+ first_reg)
                                break

                            shorturl = (returnurl(first_reg[0:count+1]))
                            if not shorturl is None:
                                break
                        n+=1
                        dictions[n] = []
                        dictions[n].append(detaildate)
                        dictions[n]+=shorturl
                        print(first_reg)
    driver.quit()
    return rmdup(dictions)

if __name__ == "__main__":

    todaydate = makedirs()                  # 그날날짜의 폴더생성 (상대경로로 만들어짐)
    dirpath = todaydate+"\\"  
    dictions = selenium_read_email()
    #dictions= {0: ['2018-08-04 03:13', 'https://bit.ly/2MiFMhY', 'http://fl0ckfl0ck.info/jul.jpg', 'jul.jpg', 36.66294097222222, 126.62258911111111, 'd89662538963f49bfaca40cbc5566da0', '19e09a58bd66872797cd896a91fd4c8e7011aebb'], 1: ['2018-08-04 07:47', 'http://bitly.kr/huvm', 'http://fl0ckfl0ck.info/ga.jpg', 'ga.jpg', 37.52779008333333, 126.90460966666667, '8bc2f709e3659e635679dce5ff9396b5', '27e6b2861bf4ef028c2e1c0f9d09582c78599e39'], 2: ['2018-08-04 08:24', 'http://bitly.kr/nZXE', 'http://fl0ckfl0ck.info/맛있어.jpg', '맛있어.jpg', 37.51306152777778, 127.05864716666666, '464e1e3242cbe60fbdb6026dc9ab32b2', '56d3b886da0c997c2a04f03b16204d240d73145e']}
    
    dictions = gpsandhash(dictions)
    makecsv(dictions)
    
    gpsdictions = readexcel(1) ## 4.각자의 엑셀읽기 
    
    googlemap(gpsdictions,1) ## 5. 구글 찍기

    gpsdictions = readexcel(2) ## 4.전체 엑셀읽기 
    
    googlemap(gpsdictions,2) ## 5. 구글 찍
    
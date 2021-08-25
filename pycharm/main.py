# coding=utf-8
import requests
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from aip import AipOcr
import time
import sys

def getOldinfo(input):
    temp=re.findall(r"oldInfo: ({[\s|\S]*}),[\s]*tipMsg",input)
    return temp

def getDef(input):
    temp = re.findall(r"def = ({[\s|\S]*});[\s]*var vm", input)
    return temp

def gethasFlag(input):
    temp = re.findall(r"hasFlag: '([\s|\S]*)',[\s]*setting", input)
    return temp

def valid(info,sfzgn):
    if info['sfjcbh']=='0':
        info['jcbhlx']=''
        info['jcbhrq']=''

    if info['sfcyglq']=='0':
        info['gllx'] = ''
        info['glksrq'] = ''

    if info['sfcxtz'] == '0':
        info['sfyyjc'] = '0'

    if info['sfyyjc'] == '0':
        info['jcjgqr'] = 0
        info['jcjg'] = ''

    if info['sfcxzysx'] == '0':
        info['qksm'] = ''

    if sfzgn == 1:
        info['szcs'] = ''
        info['szgj'] = ''

    if 'sfjxhsjc' not in info.keys() or ('sfjxhsjc' in info.keys() and info['sfjxhsjc'] != '1')  :
        info['hsjcrq'] = ''
        info['hsjcdd'] = ''
        info['hsjcjg'] = 0

    if info['sfzx'] != '1':
        info['szxqmc'] = ''
    else:
        info['bzxyy'] = ''

    if info['sfjzdezxgym'] != '1':
        info['jzdezxgymrq'] = ''

    if info['sfjzxgym'] != '1':
        info['jzxgymrq'] = ''

def construct_GeoInfo(oldInfo,adress):
    Geo_Info={}
    Geo_Info['formatted_address']=adress
    Geo_Info['addressComponent']=oldInfo['addressComponent']
    return  Geo_Info

def sendemail(msg):
    mail_host = "smtp.qq.com"
    mail_user = ""
    mail_pass = "aifxhnqlblazgjff"

    sender = ''
    receivers = ['']

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header("DiaryNote", 'utf-8')
    message['To']=Header("测试", 'utf-8')
    subject = 'DairyNote'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        #smtpObj = smtplib.SMTP()
        #连接到服务器
        #smtpObj.connect(mail_host, 25)
        smtpObj = smtplib.SMTP_SSL("smtp.qq.com")
        smtpObj.ehlo("smtp.qq.com")
        #登录到服务器
        smtpObj.login(mail_user, mail_pass)
        #发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        #退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        #打印错误
        print('error', e)

def verifyCaptcha(s,r):
    captchaID = getCaptchaID(r.text)
    if len(captchaID) == 0:
        print('\n获取captchaID 失败\n')
        sys.exit()
    else:
        captchaID = captchaID[0]
    captchaurl = "https://ua.scu.edu.cn/captcha?captchaId=" + captchaID
    r_captcha = s.get(captchaurl)
    if r_captcha.status_code == requests.codes.ok:
        with open("captcha/1.png", "wb") as file:
            file.write(r_captcha.content)
    else:
        print("\n获取验证码失败！\n")
        sys.exit()


    """ 你的 APPID AK SK """
    APP_ID = '24749844'
    API_KEY = 'x9dfGLeHRQ3nryaFFb7gGvh1'
    SECRET_KEY = 'yVbHjXSHatwVV2LhdZFWqcx7O59Dol5l'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()


    image = get_file_content('captcha/1.png')
    options={}
    options["language_type"] = "ENG"
    # res=client.basicGeneral(image)
    res=client.basicAccurate(image,options=options)

    return res['words_result'][0]['words']

def getExecution(input):
    temp = re.findall(r"<input name=\"execution\" value=\"([\s|\S]*)\"/><input", input)
    return temp

def getCaptchaID(input):
    temp = re.findall(r"id: \'([\s|\S]*)\'[\s]*};[\s]*var capt", input)
    return temp

def saveCookie(cookie):
    with open('cookies.txt',"a") as file:
        file.writelines(json.dumps(cookie.get_dict()))


def login_getCookie(s):
    f_name=open("name_password.txt","r")
    name_passowrd=f_name.readline()
    while name_passowrd is not None and name_passowrd != '':
        username=name_passowrd.split(' ')[0].replace("\n", "").replace("\r", "").strip()
        passoword=name_passowrd.split(' ')[1].replace("\n", "").replace("\r", "").strip()
        loginurl = 'https://ua.scu.edu.cn/login'
        prev_time = int(round(time.time() * 1000))
        while True:
            # 每500ms重试一次
            now_time = int(round(time.time() * 1000))
            if now_time - prev_time >= 500:
                prev_time = now_time
                r = s.get(loginurl)
                if r.status_code == requests.codes.ok:
                    print(r.cookies)
                    execution = getExecution(r.text)
                    loginData = {}
                    loginData['username'] = username
                    loginData['password'] = passoword
                    loginData['submit'] = '登录'
                    loginData['type'] = 'username_password'
                    loginData['execution'] = execution
                    loginData['_eventId'] = 'submit'

                    captcha = verifyCaptcha(s, r).replace(' ', '').strip()
                    loginData['captcha'] = captcha
                    # curr_time=time.strftime("%H:%M:%S", time.localtime())
                    # if curr_time=='9:30:00':

                    logiPagenurl = 'https://ua.scu.edu.cn/login'
                    r = s.post(logiPagenurl, data=loginData, allow_redirects=False)

                    print("\nurl is :" + logiPagenurl)
                    print(r.status_code)
                    if r.status_code == requests.codes.ok:
                        print('\n登录成功\n')
                        # print(r.text)
                        # print(r.headers)
                        # print(r.history)
                    elif r.status_code == 302:
                        print('\n页面重定向\n')
                        break
                        # print(r.text)
                        # print(r.headers)
                        # print(r.history)
                    else:
                        print('\n"error_loginpage"\n')
                        # return "error_loginpage"
                        continue

        infourl = 'https://wfw.scu.edu.cn/uc/wap/user/get-info'
        r=s.get(infourl)
        print("\infonurl is" + infourl)
        print(r.status_code)
        if r.status_code == requests.codes.ok:
            print('\n登录成功\n')
            # print(r.text)
            # print(r.headers)
            # print(r.history)
            saveCookie(s.cookies)
            return "success_savecookies"
        elif r.status_code == 302:
            print('\n页面重定向\n')
            # print(r.text)
            # print(r.headers)
            # print(r.history)
            saveCookie(s.cookies)
            return "success_savecookies"
        else:
            print('\nget-info 失败\n')
            return 'error_getinfo'
        name_passowrd = f_name.readline()



def Note(useCookie):

    geturl = 'https://wfw.scu.edu.cn/ncov/wap/default/index'
    if isinstance(useCookie, str):
        r = requests.get(geturl, cookies=json.loads(cookie_str))
    else:
        r = useCookie.get(geturl)
    # r=requests.get(geturl,headers=loginheader,cookies=getcookies)
    DEBUG = 0
    if r.status_code == requests.codes.ok:
        hasFlag = gethasFlag(r.text)[0]
        if hasFlag == '1':
            print('\n已经完成过打卡，每天只能打卡一次\n')
            sendemail('已经完成过打卡，每天只能打卡一次')
        else:
            oldInfo = getOldinfo(r.text)
            oldInfo = json.loads(oldInfo[0])
            if DEBUG:
                print("\n oldinfo is :\n")
                print(oldInfo)
            defInfo = getDef(r.text)
            defInfo = json.loads(defInfo[0])
            if DEBUG:
                print("\n definfo is :\n")
                print(defInfo)
            # 构成打卡信息
            uploadinfo = defInfo
            uploadinfo['szgjcs'] = ''
            uploadinfo['ismoved'] = '0'
            oldGeoInfo = json.loads(oldInfo['geo_api_info'])
            uploadinfo['geo_api_info'] = oldInfo['geo_api_info']
            uploadinfo['address'] = oldGeoInfo['formattedAddress']
            uploadinfo['province'] = oldGeoInfo['addressComponent']['province']
            uploadinfo['city'] = oldGeoInfo['addressComponent']['city']
            uploadinfo['area'] = uploadinfo['province'] + ' ' + uploadinfo['city'] + ' ' + \
                                 oldGeoInfo['addressComponent']['district']
            if DEBUG:
                print("\n uploadinfo is :\n")
                print(uploadinfo)

            sfzgn = 1
            valid(uploadinfo, sfzgn)
            uploadurl = 'https://wfw.scu.edu.cn/ncov/wap/default/save'
            json_data = json.dumps(uploadinfo)

            if DEBUG:
                print('\njson data is\n')
                print(json_data)

            if isinstance(useCookie, str):
                r = requests.get(geturl, cookies=json.loads(cookie_str))
            else:
                r = useCookie.get(geturl)

            if r.status_code == requests.codes.ok:
                # print(r.text)
                try:
                    print('\n打卡结果是\n')
                    print(r.json()['m'])
                    sendemail('\n打卡结果是\n' + r.json()['m'])
                except ValueError:
                    print('\n邮件服务器返回结果异常\n')
                    sendemail('邮件服务器返回结果异常')
            else:
                print('\n打卡失败！\n')
                sendemail('打卡失败')
                print(r.status_code)
                print(r.text)
    else:
        print('获取打卡页面失败')
        sendemail('获取打卡页面失败')


if __name__ == '__main__':
    #sendemail('ubuntu test')
    # res=verifyCaptcha()
    # print(res)
    loginheader={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,zh-HK;q=0.7'
    }
    f_cookie=open('cookies.txt',"r")
    cookie_str=f_cookie.readline()
    if cookie_str is None or cookie_str=='':
        s=requests.session()
        res=login_getCookie(s)
        print(res)
        if res=="success_savecookies":
            Note(s)
    else:
        while cookie_str is not None and cookie_str!='':
            Note(cookie_str)
            cookie_str=f_cookie.readline()
        f_cookie.close()

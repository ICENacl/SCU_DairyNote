import requests
import re
import json



def getOldinfo(input):
    # 先解决 config.captcha中的内容
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

if __name__ == '__main__':
    loginheader={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':'gzip, deflate, br',
        'Connection':'keep-alive',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,zh-HK;q=0.7'
    }

    getcookies={
        
    }


    geturl='https://wfw.scu.edu.cn/ncov/wap/default/index'
    r=requests.get(geturl,headers=loginheader,cookies=getcookies)
    DEBUG=0
    if r.status_code == requests.codes.ok:
        hasFlag=gethasFlag(r.text)[0]
        if hasFlag=='1':
            print('\n已经完成过打卡，每天只能打卡一次\n')
        else:
            oldInfo=getOldinfo(r.text)
            oldInfo=json.loads(oldInfo[0])
            if DEBUG:
                print("\n oldinfo is :\n")
                print(oldInfo)
            defInfo=getDef(r.text)
            defInfo=json.loads(defInfo[0])
            if DEBUG:
                print("\n definfo is :\n")
                print(defInfo)
            #构成打卡信息
            uploadinfo = defInfo
            uploadinfo['szgjcs']= ''
            uploadinfo['ismoved']='0'
            oldGeoInfo = json.loads(oldInfo['geo_api_info'])
            uploadinfo['geo_api_info'] = oldInfo['geo_api_info']
            uploadinfo['address']=oldGeoInfo['formattedAddress']
            uploadinfo['province']=oldGeoInfo['addressComponent']['province']
            uploadinfo['city']=oldGeoInfo['addressComponent']['city']
            uploadinfo['area']=uploadinfo['province']+' '+uploadinfo['city']+' '+oldGeoInfo['addressComponent']['district']
            if DEBUG:
                print("\n uploadinfo is :\n")
                print(uploadinfo)

            sfzgn=1
            valid(uploadinfo,sfzgn)
            uploadurl='https://wfw.scu.edu.cn/ncov/wap/default/save'
            json_data=json.dumps(uploadinfo)

            if DEBUG:
                print('\njson data is\n')
                print(json_data)

            r=requests.post(uploadurl,data=uploadinfo,cookies=getcookies)
            if r.status_code==requests.codes.ok:
                # print(r.text)
                try:
                    print('\n打卡结果是\n')
                    print(r.json()['m'])
                except ValueError:
                    print('\n服务器返回结果异常\n')
            else:
                print('\n打卡失败！\n')
                print(r.status_code)
                print(r.text)
    else:
        print('Cookies登录失败！')




import os
import sys
import urllib.request
import datetime
import time
import json
import pandas as pd
import numpy
import matplotlib.pyplot as plt

from matplotlib import font_manager, rc
font_path="C:\Windows\\Fonts\\batang.ttc"
font=font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

ServiceKey = "MQEi8wbM%2FhBUMFBZYB5nAzoaENMaHEyYy1dF6EDnvRNI8YyptFrbwo5ARvZsHKFkWfvHWYd57TjZQOX9N6Qw1g%3D%3D"

def getRequestUrl(url):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("[%s] Url Request Success" % datetime.datetime.now())
            return response.read().decode('utf-8')
    except Exception as e:
        print(e)
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
        return None
    
def getTourismStatsItem(yyyymm, nat_cd, ed_cd):
    service_url = "http://openapi.tour.go.kr/openapi/service/EdrcntTourismStatsService/getEdrcntTourismStatsList"
    parameters = "?_type=json&serviceKey=" + ServiceKey #인증키
    parameters += "&YM=" + yyyymm
    parameters += "&NAT_CD=" + nat_cd
    parameters += "&ED_CD=" + ed_cd

    url = service_url + parameters
    print(url) #액세스 거부 여부 확인용 출력
    responseDecode = getRequestUrl(url)
    
    if(responseDecode == None):
        return None
    else:
        return json.loads(responseDecode)
    
def getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear):
    jsonResult = []
    result = []
    natName=''
    dataEND = "{0}{1}.format(str(nEndYear), str(12))"
    ed='' #추가함
    for year in range(nStartYear, nEndYear+1):
        for month in range(1, 13):
            #if(isDataEND == 1): break # 추가
            yyyymm = "{0}{1:0>2}".format(str(year), str(month))
            jsonData = getTourismStatsItem(yyyymm, nat_cd, ed_cd) #[CODE 2]
            if (jsonData['response']['header']['resultMsg'] == 'OK'): 
                #데이터가 없는 마지막 항목인 경우 ----------------------------
                if jsonData['response']['body']['items'] == '':
                    isDataEND = 1 # 추가
                    dataEND = "{0}{1:0>2}".format(str(year), str(month-1))
                    print("데이터 없음.... \n 제공되는 통계 데이터는 %s년 %s월까지입니다." %(str(year), str(month-1)))
                    break
                #jsonData를 출력하여 확인...........................................
                print(json.dumps(jsonData, indent = 4, sort_keys = True, ensure_ascii = False))
                natName = jsonData['response']['body']['items']['item']['natKorNm']
                natName = natName.replace(' ', '')
                num = jsonData['response']['body']['items']['item']['num']
                ed = jsonData['response']['body']['items']['item']['ed']
                print('[ %s_%s : %s ]' %(natName, yyyymm, num))
                print('------------------------------------------------------')
                jsonResult.append({'nat_name': natName, 'nat_cd': nat_cd,'yyyymm': yyyymm, 'visit_cnt': num})
                result.append([natName, nat_cd, yyyymm, num])
    return (jsonResult, result, natName, ed, dataEND)

def main():
    jsonResult = []
    jsonResult2 = []
    result = []
    result2 = []
    natName='' #추가
    natName2=''
    
    print("<< 국내 입국한 외국인의 통계 데이터 수집 >>")
    nat_cd = input('국가 코드를 입력하세요(중국: 112 / 일본: 130 / 미국: 275):')
    nat_cd2 = input('국가 코드를 입력하세요(중국: 112 / 일본: 130 / 미국: 275):')

    nStartYear = int(input('데이터를 몇 년부터 수집할까요? : '))
    nEndYear = int(input('데이터를 몇 년까지 수집할까요? : '))
    ed_cd = "E" #E : 방한외래관광객, D : 해외 출국

    jsonResult, result, natName, ed, dataEND = getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear)
    jsonResult2, result2, natName2, ed, dataEND = getTourismStatsService(nat_cd2, ed_cd, nStartYear, nEndYear)
    
    if(natName==''):
        print('데이터가 전달되지 않았습니다. 공공데이터포털의 서비스 상태를 확인하기 바랍니다')
    else:
        with open('./%s_%s_%d_%s.json' % (natName, ed, nStartYear, dataEND),
                  'w',encoding='utf8') as outfile:
            jsonFile = json.dumps(jsonResult, indent = 4, sort_keys = True,
                                  ensure_ascii = False)
            outfile.write(jsonFile)
        
    columns = ["입국자국가",'국가코드','입국연월','입국자 수']
    result_df = pd.DataFrame(result, columns = columns)
    result_df.to_csv('./%s_%s_%d_%s.csv' % (natName, ed, nStartYear, dataEND), index = False, encoding = 'cp949')
    
    result2_df = pd.DataFrame(result2, columns = columns)
    result2_df.to_csv('./%s_%s_%d_%s.csv' % (natName2, ed, nStartYear, dataEND), index = False, encoding = 'cp949')

    yyyymmList=result_df["입국연월"].values.tolist()
    visitNumList=result_df["입국자 수"].values.tolist()

    yyyymmList2=result2_df["입국연월"].values.tolist()
    visitNumList2=result2_df["입국자 수"].values.tolist()

    xlabel=numpy.arange(len(yyyymmList))

    w=0.2
    plt.bar(xlabel - w, visitNumList, label=natName,color='r',width=w)
    plt.bar(xlabel, visitNumList2, label=natName2,color='b',width=w)
    plt.xticks(xlabel, yyyymmList, rotation=45)

    plt.legend(loc="upper right")
    plt.title("{0}~{1} 입국자 수".format(str(yyyymmList[0]),str(yyyymmList[-1])))
    plt.xlabel("입국연월")
    plt.ylabel("입국자 수")

    plt.show()

if __name__ == '__main__':
  main()

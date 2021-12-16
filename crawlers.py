import requests as re
from bs4 import BeautifulSoup
import json
import numpy as np
import pandas as pd
from io import BytesIO

# 웹사이트 크롤링 함수 

# comp.fnguide.com에서 단일회사 연간 재무제표 주요계정 및 재무비율 크롤링 함수 
def get_finstate_highlight_annual(stock_code):

    ''' 경로 탐색'''
    url = re.get(f'http://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{stock_code}')
    url = url.content

    html = BeautifulSoup(url,'html.parser')
    body = html.find('body')

    fn_body = body.find('div',{'class':'fng_body asp_body'})
    ur_table = fn_body.find('div',{'id':'div15'})
    table = ur_table.find('div',{'id':'highlight_D_Y'})

    tbody = table.find('tbody')



    tr = tbody.find_all('tr')

    Table = pd.DataFrame()

    for i in tr:

        # 항목 가져오기
        category = i.find('span',{'class':'txt_acd'})

        if category == None:
            category = i.find('th')   

        category = category.text.strip()


        # 값 가져오기
        value_list =[]

        j = i.find_all('td',{'class':'r'})

        for value in j:
            temp = value.text.replace(',','').strip()

            try:
                temp = float(temp)
                value_list.append(temp)
            except:
                value_list.append(0)

        Table['%s'%(category)] = value_list

        # 기간 가져오기
        thead = table.find('thead')
        tr_2 = thead.find('tr',{'class':'td_gapcolor2'}).find_all('th')
        
        
        year_list = []

        for i in tr_2:
            try:
                temp_year = i.find('span',{'class':'txt_acd'}).text
            except:
                temp_year = i.text

            year_list.append(temp_year)
        
        Table.index = year_list

    Table = Table.T

    return Table


# comp.fnguide.com에서 단일회사 연간 재무제표(bs, cis, cf) 크롤링 함수 
def get_finstate(stock_code, finstate_kind):
    
    finstate_dict = {
        "cis_y": "divSonikY",
        "cis_q": "divSonikQ",
        "bs_y": "divDaechaY",
        "bs_q": "divDaechaQ",
        "cfs_y": "divCashY",
        "cfs_q": "divCashQ",
    }
    kind = finstate_dict[finstate_kind]
    
    # 경로 탐색 
    url = re.get(f'https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{stock_code}')
    url = url.content

    html = BeautifulSoup(url,'html.parser')
    body = html.find('body')

    fn_body = body.find('div',{'class':'fng_body asp_body'})
    table = fn_body.find('div',{'id':f'{kind}'})

    tbody = table.find('tbody')
    tr = tbody.find_all('tr')

    # 기간 가져오기 
    # 테이블 컬럼 리스트 할당
    thead = table.find("thead")
    terms = thead.find("tr").find_all("th")

    columns_arr = []
    for q in terms:
        columns_arr.append(q.text)    
    columns_arr[0] = "Account"
    
    Table = pd.DataFrame(columns=columns_arr)
    
    index = 0
    for i in tr:

        # 계정과목이름 
        account_nm = i.find('span',{'class':'txt_acd'})

        if account_nm == None:
            account_nm = i.find('th')   

        account_nm = account_nm.text.strip()
        Table.loc[index, "Account"] = account_nm

        # 금액 
        value_list =[]

        values = i.find_all('td',{'class':'r'})

        for value in values:
            temp = value.text.replace(',','').strip()

            try:
                temp = float(temp)
                value_list.append(temp)
            except:
                value_list.append(0)

        Table.loc[index, columns_arr[1:]] = value_list
        
        index += 1
        
    return Table


# comp.fnguide.com에서 연도별, 분기별 재무비율 크롤링 함수 
def get_finance_ratio(stock_code, kind):    # kind: annual or quarter
    if kind == "annual":
        k = 0
    elif kind == "quarter":
        k = 1
    else:
        print("두번째 변수에 annual 또는 quarter 둘 중 하나를 입력해주세요.")
    
    # 경로 탐색 
    url = re.get(f'https://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp?pGB=1&gicode=A{stock_code}')
    url = url.content

    html = BeautifulSoup(url,'html.parser')
    body = html.find('body')

    fn_body = body.find('div',{'class':'fng_body asp_body'})
    table = fn_body.find_all('div',{'class':'um_table'})[k]

    tbody = table.find('tbody')
    tr = tbody.find_all('tr')

    # 기간 가져오기 
    thead = table.find("thead")
    terms = thead.find("tr").find_all("th")

    # 테이블 컬럼 리스트 할당
    columns_arr = []
    for q in terms:
        columns_arr.append(q.text)    
    columns_arr[0] = "Account"

    Table = pd.DataFrame(columns=columns_arr)

    index = 0
    for i in tr:

        # 계정과목이름 
        account_nm = i.find('span',{'class':'txt_acd'})

        if account_nm == None:
            account_nm = i.find('th')   

        account_nm = account_nm.text.strip()

        # 비율 종류 부분 없애기
        cle = ["안정성비율", "성장성비율", "수익성비율", "활동성비율", "성장성비율", "수익성비율"]
        if account_nm in cle:
            continue

        Table.loc[index, "Account"] = account_nm

        # 금액 
        value_list =[]

        values = i.find_all('td',{'class':'r'})

        for value in values:
            temp = value.text.replace(',','').strip()

            try:
                temp = float(temp)
                value_list.append(temp)
            except:
                value_list.append(0)

        try:
            Table.loc[index, columns_arr[1:]] = value_list
            index += 1
        except ValueError:
            pass
        
    return Table

# 한국거래소(KRX) 웹사이트에서 전종목 정보 크롤링 함수 
def get_stock_info(market, date):    # market: kospi or kosdaq or konex    # date: ex) 20211001
    # Request URL
    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    # Form Data
    parms = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false',
    }

    if market == "kospi":
        parms['mktId'] = 'STK'
    elif market == "kosdaq":
        parms['mktId'] = 'KSQ'
    elif market == "konex":
        parms['mktId'] = "KNX"
        
    # 날짜 정보
    parms['trdDd'] = date
    
    # Request Headers ()
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    }

    r = re.get(url, parms, headers=headers)

    jo = json.loads(r.text)
    df = pd.DataFrame(jo['OutBlock_1'])
    
    # 크롤링 한 데이터 테이블에서 필요한 정보만 추출하고 컬럼 명 변경해서 데이터프레임에 할당
    columns = ["종목코드", "종목명", "시장구분", "종가", "시가", "고가", "저가", "거래량", "거래대금", "시가총액", "상장주식수"]
    data = df[["ISU_SRT_CD", "ISU_ABBRV", "MKT_NM", "TDD_CLSPRC", "TDD_OPNPRC", "TDD_HGPRC", "TDD_LWPRC", "ACC_TRDVOL", "ACC_TRDVAL", "MKTCAP", "LIST_SHRS"]]
    stock_info_df = pd.DataFrame(columns=columns)
    stock_info_df[columns] = data
    
    # 금액 및 주식 수 데이터를 계산 가능하도록 콤마(,)제거하고 실수형 데이터로 변경하기
    i = 0
    while i < len(stock_info_df):
        col = stock_info_df.columns
        j = 3
        srs = stock_info_df.loc[i, ["종가", "시가", "고가", "저가", "거래량", "거래대금", "시가총액", "상장주식수"]]
        for data in srs:
            stock_info_df.loc[i, col[j]] = float(data.replace(",", ""))
            j += 1
        i += 1

    return stock_info_df


# 한국거래소(KRX) 웹사이트에서 보통주 정보 크롤링 함수 
def get_common_stock_info(market):    # market: kospi or kosdaq or konex  
    # Request URL
    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    # Form Data
    parms = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT01901',
        'share': '1',
        'csvxls_isNo': 'false',
    }

    if market == "kospi":
        parms['mktId'] = 'STK'
    elif market == "kosdaq":
        parms['mktId'] = 'KSQ'
    elif market == "konex":
        parms['mktId'] = "KNX"
        
    
    # Request Headers ()
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    }

    r = re.get(url, parms, headers=headers)

    jo = json.loads(r.text)
    df = pd.DataFrame(jo['OutBlock_1'])
    
    # 종목 정보 테이블에서 보통주만 추출하기 
    common_df = pd.DataFrame()
    i = 0
    j = 0
    while i < len(df):
        if df.loc[i, "KIND_STKCERT_TP_NM"] == "보통주":
            common_df.loc[j, ["종목코드", "종목명"]] = list(df.loc[i, ["ISU_SRT_CD", "ISU_ABBRV"]])
            j += 1
        i += 1
    
    return common_df
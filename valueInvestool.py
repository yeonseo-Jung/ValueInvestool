import requests as re
from bs4 import BeautifulSoup
import json
import numpy as np
import pandas as pd
from io import BytesIO
import time
from datetime import date, timedelta

import valueInvestool_crawlers
import valueInvestool_getData


class GetStocks:

    def __init__(self, market, date):
        # 보통주 종목정보 및 전체 종목 시세정보 할당
        common_stock = valueInvestool_crawlers.get_common_stock_info(market)
        all_stock = valueInvestool_crawlers.get_stock_info(market, date)
        # 보통주만 시세정보 할당
        # SQL inner join; preserve the order of the left keys
        # 시가총액 기준 내림차순 정렬
        stock_infos = common_stock.merge(all_stock).sort_values(by=["시가총액"], ascending=False, ignore_index=True)

        self.stock_infos = stock_infos.loc[0:9].reset_index()    #


    # 다중회사의 자본잠식률 구하는 함수
    def get_impairment(self, bs_term):
        noneType_arr = []
        zeroCapital_arr = []
        imp_df = pd.DataFrame(columns=["종목코드", "종목명", "impairment_ratio_0", "impairment_ratio_1", "impairment_ratio_2", "impairment_ratio_3"])

        i = 0
        index = 0
        while i < len(self.stock_infos):
            stock = self.stock_infos.loc[i]
            try:
                fstate_bs = valueInvestool_crawlers.get_finstate(stock["종목코드"], bs_term)
            # 해당 회사의 bs를 찾지 못했을 때 예외처리
            except AttributeError:
                i += 1
                continue

            impairments = valueInvestool_getData.get_impairment(stock, fstate_bs, index, i, imp_df, noneType_arr, zeroCapital_arr)
            imp_df = impairments[0]
            noneType_arr = impairments[1]
            zeroCapital_arr = impairments[2]
            
            i += 1
            index += 1
            
        return imp_df, noneType_arr, zeroCapital_arr









# test code 

getStock = GetStocks("kospi", "20211216")

imp = getStock.get_impairment("bs_y")

print(imp[0])
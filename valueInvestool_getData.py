import pandas as pd


# 재무제표에서 계정과목에 대한 금액 데이터 찾기 함수
def find_account(finstate, account_nm):
    i = 0
    for ac in finstate["Account"]:
        if ac == account_nm:
            return_data = finstate.loc[i]
            break
        
        # 일치하는 계정과목명이 없고 찾고자 하는 계정과목명이 포함된 계정과목이 존재하는 경우
        elif account_nm in ac:
            try:
                return_data.append(finstate.loc[i, "Account"])
            except NameError:
                return_data = []
                return_data.append(finstate.loc[i, "Account"])
        i += 1
    
    try:
        return return_data
    
    except NameError:
        pass


# 자본잠식률 구하는 함수
def get_impairment(stock_info, fstate_bs, index_imp, index_stock, imp_df, noneType_arr, zeroCapital_arr):  
    code = stock_info["종목코드"]
    name = stock_info["종목명"]
    imp_df.loc[index_imp, ["종목코드", "종목명"]] = [code, name]

    for j in range(-1, -5, -1): 
        try:
            try:
                nonOwn = find_account(fstate_bs, "비지배주주지분")[j]
            except TypeError:
                nonOwn = 0
            equity = find_account(fstate_bs, "자본")[j] - nonOwn
            capital = find_account(fstate_bs, "자본금")[j]
            impairment = (capital - equity) / capital
            # 해당 연도 컬럼에 자본잠식률 할당
            imp_df.loc[index_imp, f"impairment_ratio_{-j-1}"] = impairment

        except TypeError:
            if not list(stock_info.loc[index_stock, ["종목코드", "종목명"]]) in noneType_arr:
                noneType_arr.append(list(stock_info.loc[index_stock, ["종목코드", "종목명"]]))
                break
        except ZeroDivisionError:
            if not list(stock_info.loc[index_stock, ["종목코드", "종목명"]]) in zeroCapital_arr:
                zeroCapital_arr.append(list(stock_info.loc[index_stock, ["종목코드", "종목명"]]))
                break

    return imp_df, noneType_arr, zeroCapital_arr


# 안정성 비율 구하는 함수
# 가장 최근에 공시된 분기 기준
def get_stable_ratio(fstate_bs, fstate_cis, finance_ratio):
    # 수중유동성(현금성자산 / 월평균매출액): 초단기적 안정성 지표
    try:
        cash = find_account(fstate_bs, "현금및현금성자산")[-1]
        sales_mean = find_account(fstate_cis, "매출액")[1:5].mean() / 3
        liquidity = cash / sales_mean
    # fstate_bs 계정과목에 "현금및현금성자산" 혹은 "매출액"이 존재하지 않는다면 금융업일 가능성이 크므로 liquidity = 0으로 가정하고 넘어가자
    except TypeError:
        liquidity = 0

    # 당좌비율(당좌자산 / 유동부채): 단기적 안정성 지표
    quick_ratio = find_account(finance_ratio, "당좌비율")

    # 자기자본비율(자본총계 / 자산총계): 중장기적 안정성 지표
    equity_ratio = find_account(finance_ratio, "자기자본비율")
    
    return liquidity, quick_ratio, equity_ratio

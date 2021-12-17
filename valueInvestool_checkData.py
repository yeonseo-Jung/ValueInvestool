
# 재무데이터에 대한 기준 분석 함수

def check_impairment(impairment):
    # 자본잠식률 기준: -50 (%) 미만
    cnt = 0 
    for i in range(2, 6):
        if impairment[i] < -50:
            cnt += 1

    if cnt == 4:
        return 1
    else:
        return 0

def check_liquidity(stable_ratios):
    # 수중유동성 기준: 1.2 이상
    liquidity = stable_ratios[0]
    if liquidity > 1.2:
        return 1
    else:
        return 0

def check_quickRatio(stable_ratios):
    # 당좌비율 기준: 90(%) 이상 (최근 4분기 평균)
    quick_ratio = stable_ratios[1][5]
    if quick_ratio >= 90:
        return 1
    else:
        return 0

def check_equityRatio(stable_ratios):
    # 자기자본비율 기준: 10 (%)
    equity_ratio = stable_ratios[2][5] 
    if equity_ratio >= 10: 
        return 1
    else:
        return 0


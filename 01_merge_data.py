import pandas as pd
from MergeModule import concat_dataframe, split_made_cd

# 01. 데이터 불러오기
# sheet_name=None으로 불러오면 엑셀 파일의 모든 시트를 딕셔너리 형태로 불러온다.
# 키: sheetname, 값: 데이터프레임
df_01_to_07 = pd.read_excel("../data/reefer_data_230126.xlsx", sheet_name=None) 
df_08_and_12 = pd.read_excel("../data/reefer_data_8월_12월.xlsx", sheet_name=None)

# 02. 엑셀의 sheet들 합치기
df_concat_01_to_07 = concat_dataframe(df_01_to_07)
df_concat_08_and_12 = concat_dataframe(df_08_and_12)

# 03. 제조사별로 데이터 나누기
df_carrier_JAN_to_JUL, df_daikin_JAN_to_JUL = split_made_cd(df_concat_01_to_07) 
df_carrier_AUG_and_DEC, df_daikin_AUG_and_DEC = split_made_cd(df_concat_08_and_12)

# 04. 1월~7월과 8월, 12월 데이터를 합치기
df_carrier_JAN_to_AUG_and_DEC = pd.concat([df_carrier_JAN_to_JUL, df_carrier_AUG_and_DEC]).reset_index(drop=True)
df_daikin_JAN_to_AUG_and_DEC = pd.concat([df_daikin_JAN_to_JUL, df_daikin_AUG_and_DEC]).reset_index(drop=True)

# 05. 데이터 내보내기
df_carrier_JAN_to_AUG_and_DEC.to_csv('../data/carrier_reefer_data_01_to_08_and_12.csv', encoding='cp949', index=False)
df_daikin_JAN_to_AUG_and_DEC.to_csv('../data/carrier_reefer_data_01_to_08_and_12.csv', encoding='cp949', index=False)
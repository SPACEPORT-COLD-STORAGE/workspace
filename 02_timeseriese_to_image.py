import pandas as pd
import math
from PreprocessModule import pop_sequence_number
from pyts.image import GramianAngularField
import json
from tqdm import tqdm

# 01. 데이터 불러오기(CARRIER사 데이터만)
df = pd.read_csv('../data/carrier_reefer_data_01_to_08_and_12.csv')

# 02. 문자열을 datetime으로 변경
import datetime

df['when_created'] = df['when_created'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))

# 03. 설정 온도가 냉동이면서 변하지 않고 일정한 데이터만 추출
reefer_id_list = df['reefer_id'].unique()
temperature_list = []
for reefer_id in reefer_id_list:
    temperature_setpoint = df.loc[df['reefer_id'] == reefer_id, 'temperature_setpoint'].unique()
    if len(temperature_setpoint) == 1 and temperature_setpoint[0] < 0:
        temperature_list.append(math.floor(temperature_setpoint[0]))

# 04. 추출된 데이터에서 가장 많은 case만 사용(영하 20도인 경우가 가장 많음)
max_case = pd.Series(temperature_list).value_counts().index[0]

# 05. 설정 온도가 영하 20도인 컨테이너만 추출
reefer_id_list = df['reefer_id'].unique()
reefer_below_20 = []
for reefer_id in reefer_id_list:
    temperature_setpoint = df.loc[df['reefer_id'] == reefer_id, 'temperature_setpoint'].unique()
    if len(temperature_setpoint) == 1 and math.floor(temperature_setpoint[0]) == -20.0:
        reefer_below_20.append(reefer_id)

# 06. 찾은 컨테이더에서 DEFROST 이력이 있는 컨테이너만 추출
reefer_in_defrost = []

for reefer_id in reefer_below_20:
    operating_mode_list = list(df.loc[df['reefer_id'] == reefer_id, 'operating_mode_str'].unique())
    if "DEFROST" in operating_mode_list:
        reefer_in_defrost.append(reefer_id)

# 07. 찾은 컨테이너들의 DEFROST 이력 포함 24개의 데이터가 있는것만 추출
defrost_idx_per_reefer = {}

# 7-1. 컨테이너별 DEFROST가 발생한 인덱스 추출
for reefer_id in reefer_in_defrost:
    aa = df.loc[(df['reefer_id'] == reefer_id)].reset_index(drop=True)
    defrost_idx_per_reefer[reefer_id] = pop_sequence_number(list(aa.loc[aa['operating_mode_str'] == "DEFROST"].index))

# 7-2. DEFROST포함 24개의 로그를 만들 수 있는 것만 추출
drop_idx_list = []

for reefer_id in reefer_in_defrost:
    idx_bundle = defrost_idx_per_reefer[reefer_id]
    drop_idx_list = []
    for idx_list in tqdm(idx_bundle):
        standard_length = (24 - len(idx_list)) // 2
        if (idx_list[0] - standard_length < 0) or (idx_list[-1] + standard_length > df.loc[df['reefer_id'] == reefer_id].shape[0]):
            print(reefer_id, idx_list)
            drop_idx_list.append(idx_list)
    for idx in drop_idx_list:
        idx_bundle.remove(idx)


# 7-3. DEFROST가 발생한 인덱스의 길이를 24로 고정
to_image_idx_list = {}

for reefer_id, idx_bundle in defrost_idx_per_reefer.items():
    for i, idx_list in enumerate(idx_bundle):
        if len(idx_list) != 0:
            standard_length = (24 - len(idx_list)) // 2
            start = list(range(idx_list[0]-standard_length, idx_list[0]))
            end = list(range(idx_list[-1]+1, idx_list[-1]+standard_length+1))
            start.extend(idx_list)
            start.extend(end)
            if len(start) == 23:
                start.append(start[-1]+1)
            defrost_idx_per_reefer[reefer_id][i] = start

# 08. 시계열 데이터를 이미지로 변환하기
# 8-1. 이미지로 변환가능한 형태로 변경
concat_list_at = []
concat_list_rat = []
concat_list_sat = []

idx_list_all = []

for reefer_id, idx_bundle in defrost_idx_per_reefer.items():
    for idx_list in tqdm(idx_bundle):
        if len(idx_list) != 0 and len(idx_list) > 13:
            df_tmp = df.loc[df['reefer_id'] == reefer_id].reset_index(drop=True)
            df_tmp = df_tmp.fillna(method='ffill')
            df_for_gaf = df_tmp.loc[idx_list].reset_index(drop=True)

            idx_list_all.append([idx_list, reefer_id])

            concat_list_at.append(df_for_gaf[['ambient_temperature']].T)
            concat_list_rat.append(df_for_gaf[['return_air_temperature']].T)
            concat_list_sat.append(df_for_gaf[['supply_air_temperature']].T)

# 8-2. GASF, GADF 방식으로 변환하기
gasf = GramianAngularField(method='summation')
X_gasf_at = gasf.fit_transform(pd.concat(concat_list_at))
X_gasf_rat = gasf.fit_transform(pd.concat(concat_list_rat))
X_gasf_sat = gasf.fit_transform(pd.concat(concat_list_sat))


gadf = GramianAngularField(method='difference')
X_gadf_at = gadf.fit_transform(pd.concat(concat_list_at))
X_gadf_rat = gadf.fit_transform(pd.concat(concat_list_rat))
X_gadf_sat = gadf.fit_transform(pd.concat(concat_list_sat))

# 8-3. 변환된 데이터를 dict에 저장하기
image_data_dict = {
    "gasf_at":[X_gasf_at.tolist(), idx_list_all], 
    "gasf_rat":[X_gasf_rat.tolist(), idx_list_all],
    "gasf_sat":[X_gasf_sat.tolist(), idx_list_all],
    "gadf_at":[X_gadf_at.tolist(), idx_list_all],
    "gadf_rat":[X_gadf_rat.tolist(), idx_list_all],
    "gadf_sat":[X_gadf_sat.tolist(), idx_list_all]
}

# 09. 데이터 내보내기
with open('../data/image_data.json', 'w') as f:
    json.dump(image_data_dict, f, indent=4)
def split_made_cd(df):
    """
    데이터를 제조사에 따라 나누는 함수입니다.

    Input
    -----
    df: 데이터프레임

    Returns
    -------
    carrier, daikin: 나누어진 데이터프레임(튜플)
    """
    carrier = df.loc[df['made_cd'] == 'CARRIER']
    daikin = df.loc[df['made_cd'] == 'DAIKIN']

    return carrier, daikin


def kelvin_to_celsius(df):
    """
    데이터의 온도 관련 변수들을 섭씨온도로 변환하는 함수입니다.

    Input
    -----
    df: 온도 관련 변수들이 있는 데이터프레임

    Return
    ------
    df_celsius: 섭씨온도로 변환된 데이터프레임
    """
    df_celsius = df.copy()

    K = 273.15
    
    df_celsius['ambient_temperature'] = df['ambient_temperature'] - K
    df_celsius['return_air_temperature'] = df['return_air_temperature'] - K
    df_celsius['supply_air_temperature'] = df['supply_air_temperature'] - K
    df_celsius['temperature_setpoint'] = df['temperature_setpoint'] - K

    return df_celsius


def concat_dataframe(loaded_excel):
    """
    sheet가 여러 개인 데이터를 하나로 합치는 함수입니다.

    Input
    -----
    loaded_excel: sheet_name=None으로 불러온 딕셔너리

    Return
    ------
    concated_df: 하나로 합쳐진 데이터프레임
    """ 
    df_list = list(loaded_excel.keys())[:-2] # 알람코드와 상태정보는 삭제

    concat_list = []
    for key in df_list:
        df = kelvin_to_celsius(loaded_excel[key])
        concat_list.append(df)

    concated_df = pd.concat(concat_list)

    return concated_df
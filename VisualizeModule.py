import matplotlib.pyplot as plt

def draw_lineplot(df_list, title_list=None, flag=None):
    """
    최대 9개까지 설정온도, 공급온도, 순환온도, 제상모드, 셧다운에 대한 온도 변화를 꺽은선 그래프로 시각화하는 함수입니다.

    Inputs
    ------
    df_list: timestamp를 index로 하고 설정온도, 공급온도, 순환온도, 제상모드, 셧다운(선택)이 포함되어 있는 데이터프레임들. (최대 9개까지 가능, 하나도 가능)
    title_list: default: None, 지정할 제목이 따로 있으면 title을 리스트에 담아 넘겨주세요.
    flag: default: None, 셧다운이 포함되어 있는 데이터라면 SHUTDOWN을 넘겨주세요.
    Returns
    -------
    None: 반환값은 없고 시각화만 해줍니다.
    """

    plt.rcParams['font.family'] = 'Malgun Gothic' # 한글 폰트 설정
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 표시 설정
    plt.subplots_adjust(hspace=0.6) # 서브플롯 시 위 아래 간격 설정

    height = 10 * len(df_list) # 서브플롯 시 개수에 따라 크기가 변하므로 계산해줌.
    fig = plt.figure(figsize=(25, height))

    color_list = ['tab:blue', 'tab:orange', 'tab:red', 'tab:cyan']
    if flag == "SHUTDOWN":
        color_list = ['tab:blue', 'yellow', 'gray', 'tab:cyan', 'tab:red']

    set_space = 100*len(df_list) + 11

    for i, df in enumerate(df_list):
        globals()[f"chart_{i}"] = fig.add_subplot(set_space)
        globals()[f"chart_{i}"].margins(x=0, y=0.284) # x축은 여백없음, y축은 위로 약간의 여백 생성
        
        globals()[f"chart_{i}"].plot(df['temperature_setpoint'], '-o', color=color_list[0], label='설정온도')
        globals()[f"chart_{i}"].plot(df['supply_air_temperature'], '-o', color=color_list[1], label='공급온도')
        globals()[f"chart_{i}"].plot(df['return_air_temperature'], '-o', color=color_list[2], label='순환온도')
        globals()[f"chart_{i}"].plot(df['IS_DEFROST'], '-o', color=color_list[3], linewidth='3', label='제상모드')

        if flag == "SHUTDOWN":
            globals()[f"chart_{i}"].plot(df['IS_SHUTDOWN'], '-o', color=color_list[4], linewidth='3', label='셧다운')

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel("시간(일 시)", fontsize=14)
        plt.ylabel("온도(°C)", fontsize=14)
        if title_list == None:
            title = f"{df.index[0].year}-{df.index[0].month}-{df.index[0].day} {df['reefer_id'].unique()[0]} 컨테이너 온도 변화"
        else:
            title = title_list[i]
        plt.title(title, fontsize=18)
        plt.legend(loc='best', fontsize=14)
        plt.grid(True)
        plt.axhline(y=0, color='gray')

        set_space += 1
    plt.show()
import numpy as np

def pop_sequence_number(num_list):
    """
    DEFROST가 발생한 인덱스를 뽑아내는 함수입니다.

    Inputs
    ----------
    num_list: DEFROST가 발생한 인덱스 번호(1차원 리스트)

    Return
    ------
    packet: DEFROST가 발생한 인덱스 번호 묶음(2차원 리스트)
    """
    packet = []
    tmp = []

    v = num_list.pop(0)
    tmp.append(v)

    while (len(num_list) > 0):
        vv = num_list.pop(0)
        if v+1 == vv:
            tmp.append(vv)
            v = vv
        else:
            packet.append(tmp)
            tmp = []
            tmp.append(vv)
            v = vv
    
    packet.append(tmp)
    return packet

def is_defrost(temp_value, op_mode):
    """
    DEFROST가 발생했을 때를 시각화하기 위한 데이터를 만드는 함수입니다.
    """
    if op_mode == "DEFROST":
        return temp_value
    return np.nan
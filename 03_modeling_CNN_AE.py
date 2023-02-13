import numpy as np
from CNN_AE import ConvAutoEncoder
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import json

# 파라미터 설정
batch_size = 64
learning_rate = 0.0001
num_epoch = 50

# 01. 데이터 불러오기
with open("../data/image_data.json", "r") as f:
    image_data = json.load(f)

# 02. 데이터셋 분리하기
train_dict = {}
test_dict = {}

for key in image_data.keys():
    data = image_data[key]

    aa = []
    for i, j in zip(data[0], data[1]):
        aa.append((torch.FloatTensor([i]), j))
    aa = tuple(aa)

    train, test = train_test_split(aa, test_size=0.1, random_state=42)
    train_loader = DataLoader(train, batch_size=batch_size, shuffle=True,num_workers=2,drop_last=True)

    train_dict[key] = train_loader
    test_dict[key] = test

# 03. train, test 함수 정의
def train(train_loader, key):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = ConvAutoEncoder()
    loss_func = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    train_loss_log = []
    for i in range(num_epoch):
        train_loss = []
        for image in tqdm(train_loader):
            optimizer.zero_grad()
            image = image[0].to(device) # index는 제외하고 이미지 배열만 학습
            
            output = model(image)
            
            loss = loss_func(output,image)
            loss.backward()
            optimizer.step()
            train_loss.append(loss.item())
        print(f"{i} epochs loss: {np.mean(train_loss)}")
        train_loss_log.append(np.mean(train_loss))

    # 학습이 끝난 모델 저장
    torch.save(model, f"./cae_{key}_50.pt")
    torch.save(model.state_dict(), f"./cae_{key}_state_dict_50.pt")

    return train_loss_log, model

def test(test, model):
    test_loss_log = []
    model.eval()
    loss_func = nn.MSELoss()

    with torch.no_grad():
        for data in tqdm(test):
            image = data[0].unsqueeze(0)
            output = model(image)
            loss = loss_func(output, image)
            test_loss_log.append([loss.item(), data[1]])
        return test_loss_log

# 04. 학습
train_loss_log_dict = {}
model_dict = {}

for key, val in train_dict.items():
    train_loss_log_dict[key], model_dict[key] = train(val, key)

# 05. 예측
test_loss_log_dict = {}

for key, val in test_dict.items():
    test_loss_log_dict[key] = test(val, model_dict[key])

# 06. 분석을 위해 예측된 데이터의 loss와 데이터를 dict에 저장
final_test_data_dict = {}

for key, val in test_dict.items():
    tmp_dict = {}
    for i in range(len(val)):
          tmp_dict[i] = [val[i][0].tolist(), test_loss_log_dict[key][i]]
    final_test_data_dict[key] = tmp_dict

# 07. 내보내기
with open('../data/test_result_data.json', 'w') as f:
    json.dump(final_test_data_dict, f, indent=4) # index 0: image_array, index 1: loss
import torch.nn as nn

class ConvAutoEncoder(nn.Module):
    def __init__(self):
        super(ConvAutoEncoder, self).__init__()
        
        # Encoder
        self.layer1 = nn.Sequential(
                        nn.Conv2d(1,16,3,padding=1), # batch x 16 x 24 x 24
                        nn.ReLU(),
                        nn.BatchNorm2d(16),
                        nn.Conv2d(16,32,3,padding=1), # batch x 32 x 24 x 24
                        nn.ReLU(),
                        nn.BatchNorm2d(32),
                        nn.Conv2d(32,64,3,padding=1), # batch x 64 x 24 x 24
                        nn.ReLU(),
                        nn.BatchNorm2d(64),
                        nn.MaxPool2d(2,2) # batch x 64 x 12 x 12
        )
        self.layer2 = nn.Sequential(
                        nn.Conv2d(64,128,3,padding=1), # batch x 128 x 12 x 12
                        nn.ReLU(),
                        nn.BatchNorm2d(128),
                        nn.MaxPool2d(2,2),
                        nn.Conv2d(128,256,3,padding=1), # batch x 256 x 6 x 6
                        nn.ReLU()
        )

        # Decoder
        self.tran_cnn_layer1 = nn.Sequential(
                        nn.ConvTranspose2d(256,128,3,2,1,1), # batch x 128 x 12 x 12
                        nn.ReLU(),
                        nn.BatchNorm2d(128),
                        nn.ConvTranspose2d(128,64,3,1,1), # batch x 64 x 12 x 12
                        nn.ReLU(),
                        nn.BatchNorm2d(64)
        )
        self.tran_cnn_layer2 = nn.Sequential(
                        nn.ConvTranspose2d(64,16,3,1,1), # batch x 16 x 12 x 12
                        nn.ReLU(),
                        nn.BatchNorm2d(16),
                        nn.ConvTranspose2d(16,1,3,2,1,1), # batch x 1 x 24 x 24
                        nn.ReLU()
        )
            
            
    def forward(self, x):
        output = self.layer1(x)
        output = self.layer2(output)
        output = self.tran_cnn_layer1(output)
        output = self.tran_cnn_layer2(output)

        return output
import torch
from torch import nn
import torchvision.transforms as transforms
from predict.resnet import resnet50
from PIL import Image
import os
import json

def imageclassify(picture):
    """将上传的图片进行图片识别分类"""
    # 设置日志级别
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # 读取标签文件
    json_path = './class_indices.json'
    assert os.path.exists(json_path), "file: '{}' dose not exist.".format(json_path)
    with open(json_path, "r") as f:
        class_indict = json.load(f)

    # 加载模型
    model = resnet50(num_classes=102)
    model_weight_path = './model.pth'
    device = 'cpu'
    model.load_state_dict(torch.load(model_weight_path, map_location=device))

    # 读取图片并进行预处理
    image = Image.open(picture)
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = preprocess(image).unsqueeze(0)

    # 预测
    model.eval()
    with torch.no_grad():
        # predict class
        output = torch.squeeze(model(image.to(device))).cpu()
        predict = torch.softmax(output, dim=0)
        predict_cla = torch.argmax(predict).numpy()

    label = class_indict[str(predict_cla)]
    return label

label = imageclassify('./dangshen.jpeg')
print(label)
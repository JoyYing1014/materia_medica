from functools import lru_cache
import json

from django.conf import settings
from django.shortcuts import render
from .forms import UploadImageForm
import torch
import torchvision.transforms as transforms
from predict.resnet import resnet50
from PIL import Image


def predictindex(request):
    """图片的上传"""
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.save()
            lab = imageclassify(picture)
            return render(request, 'predict/show.html', {'picture': picture, 'label': lab})
    else:
        form = UploadImageForm()
    return render(request, 'predict/predictindex.html', {'form': form})


@lru_cache(maxsize=1)
def get_image_classifier():
    device = torch.device(settings.PREDICT_MODEL_DEVICE)
    if device.type == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('PREDICT_MODEL_DEVICE 配置为 cuda，但 CUDA 不可用。')

    with settings.PREDICT_CLASS_INDICES.open(encoding='utf-8') as file:
        class_indices = json.load(file)
    model = resnet50(num_classes=102)
    weights = torch.load(settings.PREDICT_MODEL_WEIGHTS, map_location=device, weights_only=True)
    model.load_state_dict(weights)
    model.to(device).eval()
    return class_indices, model, device

def imageclassify(picture):
    """将上传的图片进行图片识别分类"""
    class_indices, model, device = get_image_classifier()
    image = Image.open(picture.photo.path).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = preprocess(image).unsqueeze(0)

    # 预测
    model.eval()
    with torch.inference_mode():
        output = torch.squeeze(model(image.to(device))).cpu()
        predict = torch.softmax(output, dim=0)
        predict_cla = torch.argmax(predict).item()

    return class_indices[str(predict_cla)]

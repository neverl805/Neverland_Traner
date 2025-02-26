import os

import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image


preprocess = transforms.Compose([
    transforms.Resize(64),
    transforms.ToTensor()
])

device = "cuda" if torch.cuda.is_available() else "cpu"

def load_resent_model(download_path=None):
    if download_path != None:
        os.environ['TORCH_HOME'] = download_path

    resnet_model = models.resnet50(pretrained=True)
    resnet_model.to(device)
    resnet_model.eval()
    return resnet_model



def extract_features(image_path, model, transform):
    image = Image.open(image_path).convert('RGB')
    image_t = transform(image)
    batch_t = torch.unsqueeze(image_t, 0)
    with torch.no_grad():
        features = model(batch_t.to(device))
    return features


def calculate_similarity(vector1, vector2):
    similarity = torch.nn.functional.cosine_similarity(vector1, vector2)
    return similarity.item()


def resent_predict(img_path1, img_path2, resnet_model):
    # 提取两张图像的特征
    features1 = extract_features(img_path1, resnet_model, preprocess)
    features2 = extract_features(img_path2, resnet_model, preprocess)

    # 计算相似度
    similarity = calculate_similarity(features1, features2)

    return similarity


if __name__ == '__main__':

    image_path1 = R'hcp_nine\main_pic.jpg'
    image_path2 = R'hcp_nine\caec83bc-a35d-40d0-8f2c-bce63d6348b4.jpg'

    # image_path1 = R'dunshan_yzm\db_title\2.png'
    # image_path2 = R'dunshan_yzm\db_bg\0.png'

    features1 = extract_features(image_path1, resnet_model, preprocess)
    features2 = extract_features(image_path2, resnet_model, preprocess)


    similarity = calculate_similarity(features1, features2)


    print(f"The similarity between the images is: {similarity}")

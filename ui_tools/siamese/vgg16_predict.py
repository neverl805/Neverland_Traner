import os
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

# 定义预处理流程
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.ToTensor(),
])
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_vgg_model(download_dir=None):
    if download_dir != None:
        os.environ['TORCH_HOME'] = download_dir
    # 加载预训练的VGG16模型
    vgg16 = models.vgg16(pretrained=True)
    vgg16.to(device)
    # 切换到评估模式
    vgg16.eval()
    return vgg16


# 定义函数，用于提取图像的特征向量
def extract_features(img_path, model, transform):
    img = Image.open(img_path)
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)

    with torch.no_grad():
        features = model(batch_t.to(device))

    return features


# 定义函数，计算两个向量的余弦相似度
def calculate_similarity(vector1, vector2):
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    similarity = cos(vector1, vector2)
    return similarity.item()


def vgg_predict(img_path1, img_path2,vgg16):
    # 提取两张图像的特征
    features1 = extract_features(img_path1, vgg16, preprocess)
    features2 = extract_features(img_path2, vgg16, preprocess)

    # 计算并打印相似度
    similarity = calculate_similarity(features1, features2)
    # print(f"The similarity between the images is: {similarity}")
    return similarity


if __name__ == '__main__':
    # 图片路径
    img_path1 = 'path_to_your_image1.jpg'
    img_path2 = 'path_to_your_image2.jpg'

    # 提取两张图像的特征
    features1 = extract_features(img_path1, vgg16, preprocess)
    features2 = extract_features(img_path2, vgg16, preprocess)

    # 计算并打印相似度
    similarity = calculate_similarity(features1, features2)
    print(f"The similarity between the images is: {similarity}")

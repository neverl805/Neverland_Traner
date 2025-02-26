import os
import random

import ddddocr
import numpy as np
import time
import cv2



def convert_yolo(x1,y1,x2,y2,save_path,img_width,img_height):
    # 假设图像尺寸为 img_width x img_height
    # 假设 (x1, y1, x2, y2) 是物体的坐标
    # 假设 class_id 是物体的类别ID

    # img_width = 672  # 更改为你的图像宽度
    # img_height = 480  # 更改为你的图像高度

    x_center = (x1 + x2) / 2.0
    y_center = (y1 + y2) / 2.0
    width = x2 - x1
    height = y2 - y1

    # 归一化坐标
    x_center /= img_width
    y_center /= img_height
    width /= img_width
    height /= img_height

    # save_path = os.path.join(txt_path,f'{img_name[:-3]}.txt')
    # 写入.txt文件
    with open(save_path, "a") as f:
        f.write(f"0 {x_center} {y_center} {width} {height}\n")


def dddd_dectet(det,img_path,img_name=None):
    with open(img_path, "rb")as f:
        images = f.read()
    poses = det.detection(images)
    image_array = cv2.imdecode(np.array(bytearray(images), dtype='uint8'), cv2.IMREAD_UNCHANGED)
    height,width,channels = image_array.shape
    image_list = []
    for i, box in enumerate(poses):
        x1, y1, x2, y2 = box
        if x2 - x1 < 15 or y2 - y1 < 15: continue

        # font_img = image_array[y1:y2 + 1, x1:x2 + 1, :3]

        # convert_yolo(x1, y1, x2, y2,img_name)
        # random_hash = sha256(str(random.getrandbits(256)).encode()).hexdigest()[:32]
        # cv2.imwrite(os.path.join(label_path,f'{random_hash}.jpg'),font_img)
        # cv2.rectangle(image_array, (box[0], box[1]), (box[2], box[3]), (0, 0, 128), 2)
        image_list.append(box)
    return image_list,width,height
    # cv2.imshow("Rectangle", image_array)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()



if __name__ == '__main__':
    # 加载ONNX模型
    det = ddddocr.DdddOcr(det=True, show_ad=False)

    base_path = 'G:\验证码训练集\腾讯验证码\文字点选'
    image_path = os.path.join(base_path, 'image')
    txt_path = os.path.join(base_path, 'txt')
    label_path = os.path.join(base_path, '分类')


    for i in os.listdir(image_path):
        pic_path = os.path.join(image_path,i)
        print(pic_path)
        dddd_dectet(pic_path,i)

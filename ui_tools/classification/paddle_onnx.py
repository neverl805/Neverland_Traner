# -*- coding: utf-8 -*
'''
@Time     : 2023/07/27
@Author   : 14march
@Desc     :
'''
import os
import time
import PIL
import numpy
import onnxruntime
import numpy as np
import cv2
import math
from PIL import Image


class strLabelConverter(object):
    def __init__(self, alphabet):
        self.alphabet = alphabet + ' '  # for `-1` index
        self.count = 0
        self.v = 0

    def decode(self, t,preds_points, length, raw=False):
        t = t[:length]
        if raw:
            return ''.join([self.alphabet[i - 1] for i in t])
        else:
            char_list = []
            for i in range(length):
                if t[i] != 0 and (not (i > 0 and t[i - 1] == t[i])):
                    self.v += preds_points[i][t[i]]
                    self.count += 1
                    char_list.append(self.alphabet[t[i] - 1])

            return [''.join(char_list),self.v / self.count]


class WordOcr:
    def __init__(self,model_path,word_path,params):
        # 创建一个 ONNX 运行时会话，指定使用 GPU
        sess_options = onnxruntime.SessionOptions()
        self.weights = model_path
        self.sess = onnxruntime.InferenceSession(self.weights, sess_options, providers=['CUDAExecutionProvider','CPUExecutionProvider'])

        with open(word_path,encoding='utf8')as f:
            self.alphabet = [i.strip() for i in f.readlines()]
        self.converter = strLabelConverter(''.join(self.alphabet))
        self.rec_image_shape = params
        # self.rec_image_shape = [3, 48, 320]

    def resize_norm_img(self, img):
        imgC, imgH, imgW = self.rec_image_shape
        # max_wh_ratio = imgW / imgH
        # assert imgC == img.shape[2]
        # imgW = int((imgH * max_wh_ratio))

        h, w = img.shape[:2]
        ratio = w / float(h)
        if math.ceil(imgH * ratio) > imgW:
            resized_w = imgW
        else:
            resized_w = int(math.ceil(imgH * ratio))

        resized_image = cv2.resize(img, (resized_w, imgH))
        resized_image = resized_image.astype('float32')
        resized_image = resized_image.transpose((2, 0, 1)) / 255
        resized_image -= 0.5
        resized_image /= 0.5
        padding_im = np.zeros((imgC, imgH, imgW), dtype=np.float32)
        padding_im[:, :, 0:resized_w] = resized_image
        return padding_im

    def predict_ocr(self, im):
        if not isinstance(im, (bytes, numpy.ndarray, PIL.Image.Image,str)):
            raise Exception("传入图片类型错误")
        if isinstance(im, bytes):
            im = cv2.imdecode(np.array(bytearray(im), dtype='uint8'), cv2.COLOR_BGR2RGB)
            # im = cv2.imdecode(np.array(bytearray(im), dtype='uint8'), cv2.Un)
        elif isinstance(im, PIL.Image.Image):
            im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        elif isinstance(im, str):
            with open(im, "rb") as f:
                img = f.read()
            im = cv2.imdecode(np.array(bytearray(img), dtype='uint8'), cv2.COLOR_BGR2RGB)
        img = self.resize_norm_img(im)
        transformed_image = np.expand_dims(img, axis=0)

        ort_inputs = {i.name: transformed_image for i in self.sess.get_inputs()}
        preds = self.sess.run(None, ort_inputs)
        preds_points = preds[0].squeeze(axis=0)
        length = preds_points.shape[0]
        preds = preds_points.reshape(length, -1)
        # preds = softmax(preds)
        preds = np.argmax(preds, axis=1)
        preds = preds.reshape(-1)
        sim_pred = self.converter.decode(preds,preds_points, length, raw=False)
        return [sim_pred]


if __name__ == '__main__':
    start = time.time()
    with open(r"G:\svn_python\torch_test\计算题验证码\6abee1090f37ece3763687ebae7596c.jpg", "rb")as f:
        img = f.read()
    ocr = WordOcr(r'G:\svn_python\torch_test\计算题验证码\sz_caculate.onnx',r'G:\svn_python\torch_test\计算题验证码\words.txt',[3, 48, 320])
    result = ocr.predict_ocr(img)
    print(f"耗时：{time.time() - start}ms", result)

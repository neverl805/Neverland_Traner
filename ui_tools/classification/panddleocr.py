import cv2
import numpy as np
from paddleocr import PaddleOCR
import os


def paddle_ocr_det_location(ocr,image):
    with open(image, "rb")as f:
        images = f.read()

    image_array = cv2.imdecode(np.array(bytearray(images), dtype='uint8'), cv2.IMREAD_UNCHANGED)
    height, width, channels = image_array.shape

    result = ocr.ocr(image,cls=True)
    location_list = []
    if result[0]:
        for i in result[0]:
            box = [int(i[0][0][0]),int(i[0][0][1]),int(i[0][2][0]),int(i[0][2][1])]
            location_list.append(tuple(box))
    return location_list,width,height


def paddle_ocr_det_text(ocr,image):

    result = ocr.ocr(image,cls=True)
    text_list = []
    if result[0]:
        for i in result[0]:
            text_list.append(i[1])

    return text_list

if __name__ == '__main__':
    path = os.path.dirname(os.getcwd())

    ocr = PaddleOCR(lang="ch",
                use_gpu=True,
                    use_angle_cls=False,
                det_model_dir=f"{path}\model\paddle\det\ch\ch_PP-OCRv4_det_infer",
                cls_model_dir=f"{path}\model\paddle\cls\ch\ch_PP-OCRv4_cls_infer",
                rec_model_dir=f"{path}\model\paddle\\rec\ch\ch_PP-OCRv4_rec_infer"
                                )
    lis = paddle_ocr_det_text(ocr,image = r'F:\yolo相关\抖音验证码系列\douyin_text\bg\7.png')
    # print(lis)
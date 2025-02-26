import cv2
from loguru import logger
from ultralytics import YOLO

def load_model(model_path=None):
    try:
        model = YOLO(model_path)
    except Exception as e:
        logger.error(e)
        return None

    return model


def yolo_predict(model, image_path):
    try:
        image = cv2.imread(image_path)
        results = model(image, verbose=False)
        return [(results[0].names[results[0].probs.top1],float(results[0].probs.top1conf))]
    except Exception as e:
        logger.error(e)
        return None


if __name__ == '__main__':
    m = r'F:\BaiduSyncdisk\js_reverse\torch_project\temu\color.pt'
    p = r'E:\captcha_image\temu_routed\val\front\front_3_0.14090612415026205.jpg'
    model = load_model(m)
    yolo_predict(model, p)

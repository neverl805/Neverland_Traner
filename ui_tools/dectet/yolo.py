import cv2
import os
from loguru import logger
from ultralytics import YOLO, YOLOWorld

def load_model(model_type, model_path=None, labels=None):
    if labels is None:
        labels = []
    try:
        if model_type == 'base':
            # logger.info(os.getcwd())
            model = YOLOWorld(os.path.join(os.getcwd(), 'model/yolo/yolov8m-world.pt'))
            # model = YOLOWorld(r'G:\git_project\Neverland_trainer\half_model_label\model\yolo\yolov8m-world.pt')

            if len(labels) != 0:
                model.set_classes(labels)

        else:
            model = YOLO(model_path)
    except Exception as e:
        logger.error(e)
        return None

    return model


def yolo_predict(model, image_path,save_txt=False):
    try:
        logger.info(image_path)
        image = cv2.imread(image_path)
        results = model(image, save_txt=save_txt)
        result = []
        # 遍历每个检测到的对象
        for i, (box, label) in enumerate(zip(results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist())):
            # 获取 bounding box 坐标
            x1, y1, x2, y2 = map(int, box)

            # 获取标签名称
            label_name = model.names[int(label)]

            # 截取 bounding box 对应的图像区域
            cropped_image = image[y1:y2, x1:x2]
            logger.success(f'识别到的目标坐标: {[x1, y1, x2, y2]}  标签: {label_name}')
            result.append({
                'image': cropped_image,
                'label': label_name,
                'shape': results[0].orig_shape,
                'box': [x1, y1, x2, y2]
            })
    except Exception as e:
        logger.error(e)
        return []
    return result


if __name__ == '__main__':
    p = r'E:\BaiduSyncdisk\torch_project\temu\pic\04aa8b72515acc18423a26a7dddf1d2b.png'
    model = load_model('self',model_path=r'E:\BaiduSyncdisk\torch_project\temu\train26\weights\best.pt')
    yolo_predict(model, p)

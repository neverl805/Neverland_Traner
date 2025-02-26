import cv2
import numpy as np

# 随机裁剪 (Random Cropping)
def random_crop(image, crop_percent):
    height, width = image.shape[:2]
    crop_height = int(height * crop_percent)
    crop_width = int(width * crop_percent)

    top = np.random.randint(0, height - crop_height)
    left = np.random.randint(0, width - crop_width)

    bottom = top + crop_height
    right = left + crop_width

    cropped_image = image[top:bottom, left:right]
    return cropped_image


# 随机水平翻转 (Random Horizontal Flip)
def random_horizontal_flip(image, probability=0.5):
    if np.random.rand() < probability:
        image = cv2.flip(image, 1)
    return image


# 随机旋转 (Random Rotation)
def random_rotation(image, angle_range=(-10, 10)):
    angle = np.random.randint(*angle_range)
    height, width = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    return rotated_image


# 随机亮度和对比度调整 (Random Brightness and Contrast)
def random_brightness_contrast(image, brightness_range=(0.8, 1.2), contrast_range=(0.8, 1.2)):
    brightness_factor = np.random.uniform(*brightness_range)
    contrast_factor = np.random.uniform(*contrast_range)

    adjusted_image = cv2.convertScaleAbs(image, alpha=contrast_factor,
                                         beta=255 * (1 - contrast_factor) * brightness_factor)
    return adjusted_image



# 随机颜色变换 (Random Color Jittering)
def random_color_jitter(image, hue_shift_limit=(-20, 20), sat_shift_limit=(-20, 20), val_shift_limit=(-20, 20)):
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(image_hsv)

    hue_shift = np.random.randint(*hue_shift_limit)
    h = cv2.add(h, hue_shift)

    sat_shift = np.random.randint(*sat_shift_limit)
    s = cv2.add(s, sat_shift)

    val_shift = np.random.randint(*val_shift_limit)
    v = cv2.add(v, val_shift)

    image_hsv = cv2.merge((h, s, v))
    jittered_image = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)
    return jittered_image


# 随机高斯模糊
def random_gaussian_blur(image, kernel_size_range=(3, 7)):
    kernel_size = np.random.choice(np.arange(*kernel_size_range, 2))
    blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return blurred_image


# 随机椒盐噪声 (Random Salt and Pepper Noise)
def random_salt_pepper_noise(image, noise_density=0.01):
    noisy_image = image.copy()

    rows, cols = image.shape[:2]
    num_noise_pixels = int(noise_density * rows * cols)

    for _ in range(num_noise_pixels):
        y = np.random.randint(0, rows)
        x = np.random.randint(0, cols)
        noisy_image[y, x] = 0 if np.random.rand() < 0.5 else 255

    return noisy_image

# 随机剪切 (Random Shearing)
def random_shearing(image, shear_range=(-0.2, 0.2)):
    shear_factor = np.random.uniform(*shear_range)

    rows, cols = image.shape[:2]
    shear_matrix = np.float32([[1, shear_factor, 0], [0, 1, 0]])
    sheared_image = cv2.warpAffine(image, shear_matrix, (cols, rows))
    return sheared_image

# 随机缩放 (Random Scaling)
def random_scaling(image, scaling_range=(0.8, 1.2)):
    scale_factor = np.random.uniform(*scaling_range)

    rows, cols = image.shape[:2]
    scaled_size = (int(cols * scale_factor), int(rows * scale_factor))
    scaled_image = cv2.resize(image, scaled_size, interpolation=cv2.INTER_LINEAR)
    return scaled_image


# 随机平移 (Random Translation)
def random_translation(image, translation_range=(-20, 20)):
    tx = np.random.randint(*translation_range)
    ty = np.random.randint(*translation_range)

    rows, cols = image.shape[:2]
    translation_matrix = np.float32([[1, 0, tx], [0, 1, ty]])
    translated_image = cv2.warpAffine(image, translation_matrix, (cols, rows))
    return translated_image


if __name__ == '__main__':

    # 读取输入图像
    image = cv2.imread(r"F:\BaiduSyncdisk\js_reverse\torch_project\temu\pic\ae649a127d1796fceebb215386688703.png")

    # 应用数据增强方法
    cropped_image = random_crop(image, 0.8)
    flipped_image = random_horizontal_flip(image)
    rotated_image = random_rotation(image)
    adjusted_image = random_brightness_contrast(image)
    jittered_image = random_color_jitter(image)

    # 保存输出图像
    cv2.imshow("cropped_image.jpg", cropped_image)
    cv2.imshow("flipped_image.jpg", flipped_image)
    cv2.imshow("rotated_image.jpg", rotated_image)
    cv2.imshow("adjusted_image.jpg", adjusted_image)
    cv2.imshow("jittered_image.jpg", jittered_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
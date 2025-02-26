import cv2
import numpy as np

def calculate_histogram(image_path):
    # Load the image
    image = cv2.imread(image_path)
    # Convert it to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Calculate the histogram
    # The mask is set to None (indicating no mask), we use 256 bins and specify the range of HSV
    histogram = cv2.calcHist([hsv_image], [0, 1], None, [256, 256], [0, 256, 0, 256])
    # Normalize the histogram
    cv2.normalize(histogram, histogram, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    return histogram

def compare_histograms(hist1, hist2):
    # Compare the histograms using the Chi-Squared method
    distance = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
    return distance


def color_predict(image_path1, image_path2):
    # Calculate the histograms
    histogram1 = calculate_histogram(image_path1)
    histogram2 = calculate_histogram(image_path2)
    # Compare the histograms
    similarity_score = compare_histograms(histogram1, histogram2)
    return similarity_score


if __name__ == '__main__':

    # Paths to the images
    image_path1 = r'E:\python_SVN\half_model_label\half_model_label\image\siamese_picture\-6cevhBs39-5xsn.jpg'
    image_path2 = r'E:\python_SVN\half_model_label\half_model_label\image\siamese_picture\05b1a87d-30f0-4e4b-a600-3dc3571cc2a3.jpg'

    # Calculate histograms
    histogram1 = calculate_histogram(image_path1)
    histogram2 = calculate_histogram(image_path2)

    # Compare the histograms
    similarity_score = compare_histograms(histogram1, histogram2)

    # The lower the score, the more similar the histograms are
    print(f"The similarity score is: {similarity_score}")

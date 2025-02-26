import cv2
import numpy as np

def calculate_shape_descriptor(image_path):
    # Load the image in grayscale
    image = cv2.imread(image_path, 0)
    # Apply GaussianBlur to reduce image noise if it is required
    image = cv2.GaussianBlur(image, (5, 5), 0)
    # Detect edges using Canny
    edges = cv2.Canny(image, 30, 50)
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        raise ValueError("No contours found in the image")

    original_image = cv2.imread(image_path)
    cv2.drawContours(original_image, contours, -1, (0, 255, 0), 3)

    # Assuming that the largest contour corresponds to the shape of the object
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    # Calculate the moment of the largest contour
    moment = cv2.moments(contours[0])
    # Calculate Hu Moments
    huMoments = cv2.HuMoments(moment)
    # Log scale hu moments
    for i in range(0, 7):
        huMoments[i] = -1 * np.copysign(1.0, huMoments[i]) * np.log10(abs(huMoments[i]))

    # cv2.imshow('Contours', original_image)
    # cv2.waitKey(0)  # Wait for a key press to close the window
    # cv2.destroyAllWindows()
    return huMoments


def compare_shapes(huMoments1, huMoments2):
    # Calculate the difference between the two sets of Hu Moments
    distance = cv2.norm(huMoments1, huMoments2, cv2.NORM_L2)
    return distance


def shape_texture_predict(image_path1, image_path2):

    # Calculate the histograms
    histogram1 = calculate_shape_descriptor(image_path1)
    histogram2 = calculate_shape_descriptor(image_path2)

    # Compare the histograms
    similarity_score = compare_shapes(histogram1, histogram2)
    return similarity_score


if __name__ == '__main__':

    # Paths to the images
    image_path1 = r'E:\python_SVN\half_model_label\half_model_label\image\siamese_picture\-6cevhBs39-5xsn.jpg'
    image_path2 = r'E:\python_SVN\half_model_label\half_model_label\image\siamese_picture\05b1a87d-30f0-4e4b-a600-3dc3571cc2a3.jpg'

    # Calculate histograms
    histogram1 = calculate_shape_descriptor(image_path1)
    histogram2 = calculate_shape_descriptor(image_path2)

    # Compare the histograms
    similarity_score = compare_shapes(histogram1, histogram2)

    # The lower the score, the more similar the histograms are
    print(f"The similarity score is: {similarity_score}")

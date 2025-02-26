from PIL import Image



def merge_pic(image1_path, image2_path):
    # Load the images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Determine the size for the new image
    width = image1.width + image2.width
    height = max(image1.height, image2.height)

    # Create a new image with the appropriate height to store the combination
    new_image = Image.new('RGB', (width, height))

    # Paste the first image at the top
    new_image.paste(image1, (0, 0))

    # Paste the second image at the bottom
    new_image.paste(image2, (image1.width, 0))

    return new_image


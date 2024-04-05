from PIL import Image

def resize_image(image_dir):
    # Open the image
    image = Image.open('./static_data/new_examples/{}.jpg'.format(image_dir))
    
    # Resize the image to 8x8
    resized_image = image.resize((64, 64))
    
    # Return the resized image
    return resized_image


if __name__ == '__main__':
    # Test the function
    for img_id in [180, 445, 432, 478]:
        resized_image = resize_image(img_id)
        resized_image.save('resized_{}.jpg'.format(img_id))
        print('Image saved')
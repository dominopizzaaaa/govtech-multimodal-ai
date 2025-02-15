import base64

# Path to your image
image_path = "trademark_images/2003.jpg"

# Read the image and encode it in Base64
with open(image_path, "rb") as img_file:
    base64_string = base64.b64encode(img_file.read()).decode('utf-8')

# Print the Base64 string
print(base64_string)

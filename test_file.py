import base64
from PIL import Image
from io import BytesIO

# Your base64 encoded string
base64_string = ""

# Decode the base64 string
image_data = base64.b64decode(base64_string)

# Create an image from the decoded bytes
image = Image.open(BytesIO(image_data))

# Display the image
image.show()

# Save the image to a file if needed
image.save("/mnt/data/decoded_image.png")

"""

Seam Carving Helper Messenger Bot's responses strings.

Contact:Lung-Yen Chen, lungyenc@princeton.edu

"""

illegal_webhook = ("Illegal input. Please check the facebook messenger platform"
                   "settings.")

welcome_msg = ("Welcome to Seam Carving Helper! Seam carving "
               "is a content-aware image resizing application. Please send an "
               "image to start!")

def ask_new_dim(dim):
    x, y = dim
    rask_new_dim = ("The image size is " + str(x) + ","  + str(y) + ". "
                    "Please enter the new size in the format x,y. "
                    "Ex." + str(x * 9 // 10) + "," + str(y * 9 // 10) +
                    ". Or you can enter x%,y%. Ex. 80%,70%. "
                    "Or simply enter \"square\"." )
    return rask_new_dim

image_dim_wrong = "The image size is not supported. Please try another one."

image_size_wrong = "The image file size is too large. The maximum is 10MB."

image_url_wrong = ("The url is not valid or the imgae format is not supported."
                   " We support JPG/JPEG/PNG files.")

input_not_image = ("This is not an image. Please send a photo or a link to an "
                   "image.")

change_image = "Trying to change a new image. Clearing the previous image...\n"

new_dim_wrong = ("The input format is wrong or the new size of the image is"
                 "not feasible.\n")

image_missing = ("Seems like the image you sent has been gone. Please send "
                 "another one!")

wait_signal = ("Processing... it might take up to 3 minutes if the image is "
               "large...")

wait_more = ("Still processing... if it takes too long please consider "
             "resizing the image first")

thank_you_msg = ("Here you go! Thank you for using Seam Carving Helper! You "
             "can send another image to start again!")

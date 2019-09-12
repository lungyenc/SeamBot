"""

This class implements a finite state machine for the users of Seam Carving
Helper. 

Contact: Lung-Yen Chen, lungyenc@princeton.edu

"""

import requests
import queue
import io
import math
import botresponse as botRe
import seamcarving as sc
import os
from PIL import Image

class BotUser(object):
    
    s_wait_pic = 0              # Wait-for-a-pic state
    s_wait_dim = 1              # Wait-new-dimension state
    s_wait_res = 2              # Wait-for-result-pic state
    users = {}                  # Cache for the user list
    user_lim = 10000            # User limit
    q = queue.Queue(user_lim)   # Cache replacement: FIFO 
    image_size_limit = 10000000 # Image file size limit

    def __init__(self, id):
        self.id = id
        self.pic = ""
        self.state = BotUser.s_wait_pic
        self.dimX = 0
        self.dimY = 0
        if len(BotUser.users) == BotUser.user_lim:
            del users[q.get()]
        BotUser.users[id] = self
        BotUser.q.put(id)

    def get_id(self):
        return self.id

    def set_pic(self, pic):
        self.pic = pic

    def set_state(self, state):
        self.state = state

    def set_dimX(self, dimX):
        self.dimX = dimX

    def set_dimY(self, dimY):
        self.dimY = dimY

    def get_pic(self):
        return self.pic

    def get_state(self):
        return self.state

    def get_dim(self):
        return self.dimX, self.dimY

    def __str__(self):
        return ("BotUser(ID=" + str(self.id) + ", pic addr=" + self.pic + 
                ", in state= " + str(self.state) + " dim=" + 
                self.get_dim_str()  + ")")

    def get_dim_str(self):
        return str(self.dimX) + ", " + str(self.dimY)

    # Analyze if the input text is valid
    # Format: (1) x,y  (2) x%, y%  (3) square
    # It ignores any leading or tailing zeros for x or y
    # It also support any lowercase or uppercase input for (3)
    def handle_new_size(self, new_size):
        new_size = new_size.strip()
        if new_size[-1] == ".":
            new_size = new_size[0 : len(new_size) - 1]
            new_size = new_size.strip()
        if new_size.lower().startswith("square"):
            newDim = min(self.dimX, self.dimY)
            return newDim, newDim
        else:
            new_size_split = new_size.split(",")
            if len(new_size_split) != 2:
                return -1, -1
            new_size_split[0] = new_size_split[0].strip()
            new_size_split[1] = new_size_split[1].strip()
            if new_size_split[0].isdigit() and new_size_split[1].isdigit():
                newX = int(new_size_split[0])
                newY = int(new_size_split[1])
                if (newX <= self.dimX and newX > 0 and 
                    newY <= self.dimY and newY > 0):
                    return newX, newY
            elif (new_size_split[0].count("%") == 1 and 
                  new_size_split[1].count("%") == 1):
                new_size_split[0] = \
                    new_size_split[0][0 : new_size_split[0].find("%")].strip()
                new_size_split[1] = \
                    new_size_split[1][0 : new_size_split[1].find("%")].strip()
                newX = BotUser.to_float(new_size_split[0])
                newY = BotUser.to_float(new_size_split[1])
                if newX <= 100 and newY <= 100:
                    newX = math.floor(self.dimX * newX / 100)
                    newY = math.floor(self.dimY * newY / 100)
                    if newX > 0 and newY > 0:
                        return newX, newY
            return -1, -1
    
    @staticmethod
    def to_float(x):
        try:
            float(x)
            return float(x)
        except ValueError:
            return -1

    @staticmethod
    def next_state(id, message):
        user = BotUser.get_user(id)
        # need to handle cant find id situation...
        if user.get_state() == BotUser.s_wait_pic:
            if message["type"] == "image":
                image_check = BotUser.is_url_image(message["data"])
                if image_check == 0:
                    user.set_pic(message["data"])
                    user.set_state(BotUser.s_wait_dim)
                    dX, dY = BotUser.url_image_size(message["data"])
                    if dX > 0 and dY > 0:
                        user.set_dimX(dX)
                        user.set_dimY(dY)
                        # generate response message for asking the dimension
                        return BotUser.gen_res("text", 
                                botRe.ask_new_dim(user.get_dim()))
                    else:
                        # generate response saying the image size is not 
                        # supported
                        return BotUser.gen_res("text", botRe.image_dim_wrong)
                elif image_check == 1:   
                    # generate repsonse saying the image file size is too big
                    # and hence not supported
                    return BotUser.gen_res("text", botRe.image_size_wrong)
                else:
                    # generate response saying the image url is invalid
                    return BotUser.gen_res("text", botRe.image_url_wrong)
            else:
                # generate response saying the image url is invalud
                return BotUser.gen_res("text", botRe.input_not_image)
        elif user.get_state() == BotUser.s_wait_dim:
            if message["type"] == "image":
                user.set_state(BotUser.s_wait_pic)
                response = BotUser.next_state(id, message)
                response["data"] = botRe.change_image + response["data"]
                return response
            elif message["type"] == "text":
                newX, newY = user.handle_new_size(message["data"])
                if newX > 0 and newY > 0:
                    image_raw = BotUser.get_image(user.pic)
                    user.set_state(BotUser.s_wait_res)
                    if image_raw is None:
                        user.set_state(BotUser.s_wait_pic)
                        return BotUser.gen_res("text", botRe.image_missing)
                    else:
                        # call seam carving subrotuine
                        new_file_path = (os.environ.get("SC_IMG_LOC") + 
                                str(user.id) +
                                "sc.png")
                        sc.seam_carve(image_raw, new_file_path, newX, newY)
                        user.set_state(BotUser.s_wait_pic)
                        return BotUser.gen_res("image", new_file_path)
            # generate response saying the new size is not valid
            return BotUser.gen_res("text", botRe.new_dim_wrong + 
                    botRe.ask_new_dim(user.get_dim()))
        else:
            return BotUser.gen_res("text", botRe.wait_more)
                

    @staticmethod
    def is_url_image(image_url):
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        try:
            r = requests.head(image_url)
        except requests.exceptions.RequestException as e:
            print (e)
            return 2
        if "content-type" in r.headers and "Content-length" in r.headers:
            if r.headers["content-type"] in image_formats:
                if int(r.headers["Content-length"]) < BotUser.image_size_limit:
                    return 0 # image ok 
                else:
                    return 1 # image size exceeds the limit
            else:
                return 2
        return 2 # image url is not valid or the format is not supported

    @staticmethod
    def url_image_size(image_url):
        try:
            image_raw = requests.get(image_url)
        except requests.exceptions.RequestException as e:
            print (e)
            return 0, 0
        image = Image.open(io.BytesIO(image_raw.content))
        width, height = image.size
        return width, height 

    @staticmethod
    def get_image(image_url):
        try:
            image_raw = requests.get(image_url)
        except requests.exceptions.RequestException as e:
            print (e)
            return None
        return image_raw

    @staticmethod
    def gen_res(type, response):
        reply = {"type": type,
                "data": response
                }
        return reply

    @staticmethod
    def get_user_list():
        print(BotUser.users)

    @staticmethod
    def has_user(id):
        return id in BotUser.users

    @staticmethod
    def get_user(id):
        if not id in BotUser.users:
            newBotUser = BotUser(id)
        return BotUser.users[id]

    @staticmethod
    def create_user(id):
        if id in BotUser.users:
            del BotUser.users[id]
        newBotUser = BotUser(id)

    @staticmethod
    def wait_signal(id, message):
        user = BotUser.get_user(id)
        if user.get_state() == BotUser.s_wait_dim and message["type"] == "text":
            newX, newY = user.handle_new_size(message["data"])
            if newX > 0 and newY > 0:
                return True
        return False
            


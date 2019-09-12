"""

This module is a messenger for Seam Carving Helper Messenger Bot.
It handles the recieved webhook message from facebook and replies to the users.

Contact: Lung-Yen Chen, lungyenc@princeton.edu

"""

import os, json, requests
from requests_toolbelt import MultipartEncoder as Mcoder
import botresponse as botRe

# Unpack a received message from a Facebook webhook event
def unpack_msg(payload):
    
    data = json.loads(payload)
    #print("Printing the raw json message")
    #print(data)
    msg = data["entry"][0]["messaging"]
    
    for event in msg:
        sender_id = event["sender"]["id"]

        # Exception, not a message nor a "get-started" button event.
        if "message" not in event and "postback" not in event:
            print(botRe.illgeal_webhook)
            return sender_id, None

        # Get-started button pressed. Extract the new user info.
        elif "postback" in event:
            #print("postback event triggerd!")
            yield sender_id, {"type":"newUser", "data": ""}

        # Text input, can be the url to an image or the new dimension size.
        # Extarct the text.
        elif "message" in event and "text" in event["message"]:
            data = event["message"]["text"]
            data_prefix = data[0: min(len(data), len("https://"))]
            if (data_prefix.lower().startswith("http://") or 
                data_prefix.lower().startswith("https://")):
                yield sender_id, {"type":"image", "data": data}
            else:
                yield sender_id, {"type":"text", "data": data}

        # Image attachement input. Extract the url.
        elif ("attachments" in event["message"] and 
              "image" == event["message"]["attachments"][0]["type"] and 
            "sticker_id" not in event["message"]["attachments"][0]["payload"]):
            image_url = event["message"]["attachments"][0]["payload"]["url"]
            yield sender_id, {"type":"image","data": image_url}
            
        else:
            yield sender_id, {"type":"invalid","data": "", 
                    ":message_id": event["message"]["mid"]}

# Send a message to Facebook via a webhook event
def send_msg(token, user_id, response): 
    if  response["type"] != "image":
        reply_webhook_msg = {"recipient": {"id": user_id},
                             "message": {"text": response["data"]}
        }
        r = requests.post("https://graph.facebook.com/v4.0/me/messages",
                           params={"access_token": token},
                           data = json.dumps(reply_webhook_msg),
                           headers={"Content-type": "application/json"})
 
    else:
        reply_webhook_msg = {
            "recipient": json.dumps({
                "id": user_id
            }),
            "message": json.dumps({
                "attachment": {
                    "type": "image",
                    "payload": {}
                }
            }),
            "filedata": (os.path.basename(response["data"]), 
                open(response["data"], "rb"), "image/png")  
        }
        multipart_data = Mcoder(reply_webhook_msg)
        r = requests.post("https://graph.facebook.com/v4.0/me/messages",
                           params={"access_token": token},
                           data = multipart_data,
                           headers={"Content-type": multipart_data.content_type})
 
    if r.status_code != requests.codes.ok:
        print (r.text)

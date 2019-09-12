"""

Facebook messneger bot for Seam Carving Helper
This webhook server lisents to the webhook event from facebook and send
message back to the user. The bot first asks for an image that the user
wants to do seam carving with, and ask for the new dimension of the
image. 

Contact: Lung-Yen Chen, lungyenc@princeton.edu
  
"""

import sys, os, traceback, json, requests, threading
from flask import Flask, request, abort
import botmessenger as msgr
from botuser import BotUser
import botresponse as botRe

# Flask application creation
app = Flask(__name__)

# Retrieve access tokens from environment vailables
PAT = os.environ.get("PAT")
VERIFICATION_TOKEN = os.environ.get("FB_AT")

# Facebook webhook handshake singals verification
@app.route('/', methods=['GET'])
def verify_token():
    print ("Verification processing...")
    if request.args.get("hub.verify_token") == VERIFICATION_TOKEN:
        print ("Webhook verified with the correct token")
        return request.args.get("hub.challenge")
    else:
        print ("Wrong token recieved. Verification procedure failed.")
        return "Wrong verification token."

# Process recieved messages
@app.route('/', methods=['POST'])
def recieve_messages():
    payload = request.get_data()

    # Handle messages
    for sender_id, message in msgr.unpack_msg(payload):
        # Start processing valid requests
        try:
            if (message["type"] != "newUser" and BotUser.has_user(sender_id)):
                if BotUser.wait_signal(sender_id, message) is True:
                    msgr.send_msg(PAT, sender_id, 
                            BotUser.gen_res("text", botRe.wait_signal))
                    t = threading.Thread(target = process_and_reply,
                            args = (sender_id, message))
                    t.start()
                else:    
                    response = BotUser.next_state(sender_id, message)
                    msgr.send_msg(PAT, sender_id, response)
            else:
                BotUser.create_user(sender_id)
                response = {"type": "text", "data": botRe.welcome_msg}
                msgr.send_msg(PAT, sender_id, response)
        except Exception as e:
            print (e)
            traceback.print_exc()
    return "ok"

def process_and_reply(sender_id, message):
    response = BotUser.next_state(sender_id, message)
    msgr.send_msg(PAT, sender_id, response)
    msgr.send_msg(PAT, sender_id, BotUser.gen_res("text", botRe.thank_you_msg))
    os.remove(response["data"])

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port= 5000,  ssl_context=(os.environ.get("CERT"),
                                                        os.environ.get("KEY")))
    



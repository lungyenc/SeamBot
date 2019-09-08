#
# Simple webhook application
#
# Practice
#

from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/webhook', methods = ['POST'])
def webhook():
    if request.method == 'POST':
        print(request.json)
        print('-----------')
        return '', 200
    else:
        about(400)


if __name__ == '__main__':
    app.run()



# -*- coding: utf-8 -*- 

import json, base64

from flask import Flask, request, make_response, redirect
from Crypto.Cipher import AES

from config import *


app = Flask(__name__)

#

@app.route('/')
def click_tracker():
    return "click_tracker"


# input:  nyy{url: xx, seq: 1, trace_type: 1}
# output: {ret: OK, seq: 1, url_wrapper: yy}
@app.route('/wrap', methods=['POST'])
def wrap():
    jn = request.get_json(force=True)
    print "get_json", jn

    nyy = try_get_nyy_data(jn)
    print "nyy", nyy
    if not nyy:
        return gen_error("nyy format err")

    appid, sign, data = nyy
    data = try_get_wrap_data(data)
    if not data:
        return json.dumps("wrap data err", appid)

    seq, url, trace_type, uid, task_type = data
    print "url=", url
    try:
        en = url_encode(url, trace_type, uid, task_type)
    except Exception as err:
        print err

    wrapper = "{0}{1}".format(DOMAIN, en)
    return wrapper


@app.route('/ct/<path:wrapper>')
def tracing(wrapper):
    print "wrapper =", wrapper
    url, _, uid, task_type = url_decode(wrapper)
    resp = make_response(redirect(url))
    if not request.cookies.get("ct"):
        resp.set_cookie('ct', '1')
        # report
        print "report"
    else:
        print "cheat"
    return resp


###

# trace_type = 1 --> [url, trace_type, uid, task_type] 
def url_encode(*args):
    s = json.dumps(args)
    y = (16 - len(s) % 16) + len(s)
    obj = AES.new(KEY, AES.MODE_ECB)
    return "L{0}".format(base64.b64encode(obj.encrypt(s.ljust(y))))


def url_decode(en):
    en = en[1:]
    ecb = base64.b64decode(en)
    obj = AES.new(KEY, AES.MODE_ECB)
    jn = obj.decrypt(ecb).strip()
    return json.loads(jn)


def gen_error(ret, appid=0, sign=""):
    return json.dumps({"appId": appid, "sign": sign, "data": {"ret": ret}})


def try_get_wrap_data(data):
    url = data.get("url")
    seq = data.get("seq")
    trace_type = data.get("trace_type")
    meta_data = data.get("meta_data")
    if url and trace_type and meta_data:
        uid = meta_data.get("uid")
        task_type = meta_data.get("task_type")
        if uid and task_type:
            return seq, url, trace_type, uid, task_type
    return False


def try_get_nyy_data(dt):
    try:
        appid = dt.get("appId")
        sign = dt.get("sign")
        data = dt.get("data")
        print appid, "-", sign, "-", data
        if appid and (data is not None):
            return appid, sign, data
        return False
    except Exception as err:
        print "check_wrap_data err:", err
        return False


def nyy_encode(data):
    pass

def nyy_decode(jn):
    nyy = json.loads(jn)
    return nyy.get("data")


if __name__ == '__main__':
    app.run()


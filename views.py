# -*- coding: utf-8 -*- 

import json, base64, random, time

from flask import Flask, request, make_response, redirect
from Crypto.Cipher import AES
import requests

from config import *
from app_task_compat_pb2 import *

app = Flask(__name__)


@app.route('/')
def click_tracker():
    return "click_tracker"


# input:  nyy{url: xx, seq: 1, trace_type: 1, meta_data:{uid: 50, task_type: 1}}
# output: nyy{ret: OK, seq: 1, wrapper: yy}
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
        return gen_error("wrap data err", appid)

    seq, url, trace_type, uid, task_type = data
    print "url=", url
    en = url_encode(url, trace_type, appid, uid, task_type)

    wrapper = "{0}{1}".format(DOMAIN, en)
    ret = json.dumps({"appId": appid,
                        "sign": sign,
                        "data": {"ret": "OK", "seq": seq, "wrapper": wrapper}})
    return ret


@app.route('/ct/<path:wrapper>')
def tracing(wrapper):
    print "wrapper =", wrapper
    url, _, appid, uid, task_type = url_decode(wrapper)
    resp = make_response(redirect(url))
    if not request.cookies.get("ct"):
        resp.set_cookie('ct', '1')
        report_compat_action(appid, uid, task_type)
        print "report"
    else:
        print "dup"
        report_compat_action(appid, uid, task_type) # test
    return resp


###

# encode rule:
#  1) make list: [url, trace_type, appid, uid, task_type] 
#  2) turn the list into json
#  3) encrypt the json string by AES
#  4) encode the result by base64
#  5) joint the letter "L" in front of the b64 string
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


def report_compat_action(appid, uid, task_type):
    req = ReportReq()
    req.task_type = task_type
    req.report_seq = random.randint(0, int(time.time()))
    req.amount = 1

    pb = ReqProto()
    pb.uri = REPORT_REQ
    pb.appid = appid
    pb.subsid = 0
    pb.seq = 0
    pb.version = 1
    pb.report_req.MergeFrom(req)

    bin = pb.SerializeToString()
    s = base64.b64encode(bin)
    jn = json.dumps({"uid": uid, "pb": s})

    resp = requests.post(REPORT_TASK_COMPAT_ADDR, jn)
    if not resp.ok:
        print "REPORT FAIL:", resp.status_code, resp.text
    print resp.text




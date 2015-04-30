# -*- coding: utf-8 -*- 

import json, base64, random, time, logging

from flask import request, make_response, redirect
from Crypto.Cipher import AES
import requests

import cache
from config import *
from app_task_compat_pb2 import *


logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)


# input:  nyy{url: xx, seq: 1, trace_type: 1, meta_data:{uid: 50, task_type: 1}}
# output: nyy{ret: OK, seq: 1, wrapper: yy}
#@app.route('/wrap', methods=['POST'])
def wrap():
    jn = request.get_json(force=True)
    logging.debug("get_json: %s", jn)

    nyy = try_get_nyy_data(jn)
    if not nyy:
        return gen_error("nyy format err")

    appid, sign, data = nyy
    data = try_get_wrap_data(data)
    if not data:
        return gen_error("wrap data err", appid)

    seq, url, trace_type, uid, task_type = data
    if not check_url(url):
        return gen_error("invalid http url", appid, seq=seq)
    en = url_encode(url, trace_type, appid, uid, task_type)

    wrapper = "{0}{1}".format(DOMAIN, en)
    ret = json.dumps({"appId": appid,
                        "sign": sign,
                        "data": {"ret": "OK", "seq": seq, "wrapper": wrapper}})
    logging.info("wrap ret: %s", ret)
    return ret


#@app.route('/ct/<path:wrapper>')
def tracing(wrapper):
    de = url_decode(wrapper)
    if not de:
        return "X"
    url, _, appid, uid, task_type = de
    resp = make_response(redirect(url))
    if not request.cookies.get(wrapper) and not cache.is_visit(request.remote_addr):
        resp.set_cookie(wrapper, "L")
        cache.markip(request.remote_addr)
        report_compat_action(appid, uid, task_type)
        logging.info("trace done: %s, %s, %s, %s", url, appid, uid, task_type)
    else:
        logging.warn("dup trace: %s", url)
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
    try:
        en = en[1:]
        ecb = base64.b64decode(en)
        obj = AES.new(KEY, AES.MODE_ECB)
        jn = obj.decrypt(ecb).strip()
        return json.loads(jn)
    except Exception as err:
        logging.debug("url decode err: %s", err)
        return False


def check_url(url):
    return url.startswith("http")


def gen_error(ret, appid=0, sign="", seq=0):
    return json.dumps({"appId": appid, "sign": sign, "data": {"ret": ret, "seq": seq}})


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
        if appid and (data is not None):
            return appid, sign, data
        return False
    except Exception as err:
        logging.error("try_get_nyy_data err: %s", err)
        return False


def report_compat_action(appid, uid, task_type):
    req = ReportReq()
    req.task_type = int(task_type)
    req.report_seq = random.randint(0, int(time.time()))
    req.amount = 1

    pb = ReqProto()
    pb.uri = REPORT_REQ
    pb.appid = int(appid)
    pb.subsid = 0
    pb.seq = 0
    pb.version = REPORT_VERSION
    pb.report_req.MergeFrom(req)

    bin = pb.SerializeToString()
    s = base64.b64encode(bin)
    jn = json.dumps({"uid": uid, "pb": s})

    resp = requests.post(REPORT_TASK_COMPAT_ADDR, jn)
    if not resp.ok:
        logging.error("REPORT FAIL: %s, %s", resp.status_code, resp.text)



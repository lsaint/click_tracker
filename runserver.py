#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from flask import Flask
from views import *
from config import *


app = Flask(__name__)
app.add_url_rule("/wrap", "wrap", wrap, methods=["POST"])
app.add_url_rule("/ct/<path:wrapper>", "tracing", tracing)


if __name__ == '__main__':
    app.run(debug=IS_DEBUG, host=HOST)

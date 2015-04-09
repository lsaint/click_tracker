#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from views import app
from config import HOST

if __name__ == '__main__':
    app.run(host=HOST)

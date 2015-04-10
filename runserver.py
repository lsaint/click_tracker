#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from views import app
from config import *

if __name__ == '__main__':
    app.run(debug=IS_DEBUG, host=HOST)

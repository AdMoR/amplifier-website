# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from industrie_futur import app
import logging
app.logger.setLevel(logging.DEBUG)
app.run(debug=True)

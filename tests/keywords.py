#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from _helpers import TestHelpers
helpers=TestHelpers()
helpers.add_relative_path()

from lib.nlp import NLP

text = '''
The titular threat of The Blob has always struck me as the ultimate movie
monster: an insatiably hungry, amoeba-like mass able to penetrate
virtually any safeguard, capable of--as a doomed doctor chillingly
describes it--"assimilating flesh on contact.
Snide comparisons to gelatin be damned, it's a concept with the most
devastating of potential consequences, not unlike the grey goo scenario
proposed by technological theorists fearful of
artificial intelligence run rampant.
'''

nlp=NLP(text)
# print nlp
nlp.keywords()
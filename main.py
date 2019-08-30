import sys
import os
from scrapy.cmdline import execute

# import pdb; pdb.set_trace()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "sep_spider"])




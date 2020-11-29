# Third party library imports
import threading
import pandas as pd
import time

# Local library imports
from depop import search
from depop import config as cf

# Run main program
if __name__ == '__main__':

    x = cf.ConfigLoader('depop/config/search_config.ini')
    args = x.get_all_queries()

    for search_section in args.keys():

        search_object = search.Search(**args[search_section])
        t = threading.Thread(target = search_object.run_timed_search)
        t.start()



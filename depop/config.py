# Standard library imports
import configparser


class ConfigLoader:

    """ This class that loads a specific configuration file.
        Any instance of this class provides a get_all_queries function which returns a nested dictionary for each
        'search_xxx' defined in the input file.
    """

    def __init__(self, config_file):

        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.search_sections = self.config.sections()[:-2]
        self.all_search_dict = self.config.__dict__['_sections']

        self.blacklist_users = self._get_field_from_section('blacklist', 'users')
        self.blacklist_terms = self._get_field_from_section('blacklist', 'desc_terms')


    def _get_field_from_section(self, section, field):

        field = self.all_search_dict[section][field]
        field = field.split(", ")

        # if(len(field) == 1):
        #     field = field[0]

        return(field)


    def _get_search_query(self, section):

        query = self._get_field_from_section(section, 'query')
        sizes = self._get_field_from_section(section, 'sizes')
        min_price = self._get_field_from_section(section, 'min_price')
        max_price = self._get_field_from_section(section, 'max_price')
        interval = self._get_field_from_section(section, 'interval')

        filter_desc = self._get_field_from_section(section, 'filter_desc') + self.blacklist_terms
        filter_desc = [x for x in filter_desc if x]

        blacklist_users = self.blacklist_users

        if(query[0] == ''):
            raise ValueError(section + ' search query blank or invalid.')

        if(sizes[0] == ''):
            sizes = self._get_field_from_section('defaults', 'sizes')

        if(min_price[0] == ''):
            min_price = self._get_field_from_section('defaults', 'min_price')

        if(max_price[0] == ''):
            max_price = self._get_field_from_section('defaults', 'max_price')

        if(interval[0] == ''):
            interval = self._get_field_from_section('defaults', 'interval')

        search_query = locals()
        search_query.pop('self')
        search_query.pop('section')
        return(search_query)


    def get_all_queries(self):

        all_queries = dict((section, self._get_search_query(section)) for section in self.search_sections)

        for section in self.search_sections:
            all_queries[section]['query'] = all_queries[section]['query'][0]
            all_queries[section]['min_price'] = float(all_queries[section]['min_price'][0])
            all_queries[section]['max_price'] = float(all_queries[section]['max_price'][0])
            all_queries[section]['interval'] = 60*float(all_queries[section]['interval'][0])

        return(all_queries)

# x = ConfigLoader('depop/config/search_config.ini')
# x.get_all_queries()['search_001']
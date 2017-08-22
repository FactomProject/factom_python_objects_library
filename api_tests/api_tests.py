from api_objects.api_objects_factomd import APIObjectsFactomd
import unittest

from nose.plugins.attrib import attr
import re

from helpers.cli_methods import get_data_dump_from_nonansible_server
from helpers.helpers import read_data_from_json
import logging

@attr(api=True)
class APITests(unittest.TestCase):

    def setUp(self):
        self.factom_api = APIObjectsFactomd()
        data = read_data_from_json('addresses.json')
        self.factomd_address = data['factomd_controlpanel']

    def test_directory_blocks(self):
        keymr = self.factom_api.get_directory_block_head()
        self.assertTrue('000000000000000000000000000000000000000000000000000000000000000a' ==
                        self.factom_api.get_directory_block_by_keymr(keymr)["entryblocklist"][0]['chainid'])

    def test_get_heights(self):
        self.assertTrue('entryheight' in self.factom_api.get_heights())

    def test_get_blocks_by_heights(self):
        heights = self.factom_api.get_heights()
        directory_block_height = heights['directoryblockheight']
        self.assertTrue('keymr' in self.factom_api.get_directory_block_by_height(directory_block_height))

    def test_get_current_minute(self):
        datadump = get_data_dump_from_nonansible_server(self.factomd_address)
        datadumplist = datadump.split('/')
        temp = datadumplist[4]
        controlpanel_minute = int(re.search('[0-9]', temp).group())
        result = self.factom_api.get_current_minute()
        cli_minute = result['minute']
        diff =  cli_minute - controlpanel_minute
        self.assertFalse(diff > 2,"minutes are not matching")

    def test_get_pending_entries(self):
        self.factom_api.get_pending_entries()



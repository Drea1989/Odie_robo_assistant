import re

from odie.core import Utils
from odie.core.ConfigurationManager import YAMLLoader
from odie.core.Models.Dna import Dna


class InvalidDNAException(Exception):
    pass

VALID_DNA_MODULE_TYPE = ["action", "stt", "tts", "wakeon"]


class DnaLoader(object):

    def __init__(self, file_path):
        """
        Load a DNA file and check the content of this one
        :param file_path: path the the DNA file to load
        """
        self.file_path = file_path
        if self.file_path is None:
            raise InvalidDNAException("[DnaLoader] You must set a file")

        self.yaml_config = YAMLLoader.get_config(self.file_path)
        self.dna = self._load_dna()

    def get_yaml_config(self):
        """
        Class Methods which loads default or the provided YAML file and return it as a String
        :return: The loaded DNA YAML file
        :rtype: String
        """
        return self.yaml_config

    def get_dna(self):
        """
        Return the loaded DNA object if this one is valid
        :return:
        """
        return self.dna

    def _load_dna(self):
        """
        retur a DNA object from a loaded yaml file
        :return:
        """
        new_dna = None
        if self._check_dna_file(self.yaml_config):
            new_dna = Dna()
            new_dna.name = self.yaml_config["name"]
            new_dna.module_type = self.yaml_config["type"]
            new_dna.author = self.yaml_config["author"]
            new_dna.odie_supported_version = self.yaml_config["odie_supported_version"]
            new_dna.tags = self.yaml_config["tags"]

        return new_dna

    @staticmethod
    def _check_dna_file(dna_file):
        """
        Check the content of a DNA file
        :param dna_file: the dna to check
        :return: True if ok, False otherwise
        """
        success_loading = True
        if "name" not in dna_file:
            Utils.print_danger("The DNA of does not contains a \"name\" tag")
            success_loading = False

        if "type" not in dna_file:
            Utils.print_danger("The DNA of does not contains a \"type\" tag")
            success_loading = False

        else:
            # we have a type, check that is a valid one
            if dna_file["type"] not in VALID_DNA_MODULE_TYPE:
                Utils.print_danger("The DNA type %s is not valid" % dna_file["type"])
                Utils.print_danger("The DNA type must be one of the following: %s" % VALID_DNA_MODULE_TYPE)
                success_loading = False

        if "odie_supported_version" not in dna_file:
            Utils.print_danger("The DNA of does not contains a \"odie_supported_version\" tag")
            success_loading = False
        else:
            # odie_supported_version must be a non empty list
            if not isinstance(dna_file["odie_supported_version"], list):
                Utils.print_danger("odie_supported_version is not a list")
                success_loading = False
            else:
                if not dna_file["odie_supported_version"]:
                    Utils.print_danger("odie_supported_version cannot be empty")
                    success_loading = False
                else:
                    for supported_version in dna_file["odie_supported_version"]:
                        # check if major version is provided
                        if not re.search('^[\d]*[.][\d]*$', str(supported_version)):
                            Utils.print_danger("odie_supported_version cannot handle this format of version %s. "
                                               "Only major version should be provided" % supported_version)
                            success_loading = False


        return success_loading

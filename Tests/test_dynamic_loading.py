import inspect
import os
import unittest


class TestDynamicLoading(unittest.TestCase):

    """
    Test case for dynamic loading of python class
    This is used to test we can successfully import:
    - STT engine
    - TTS engine
    - Wakeon engine
    - All core actions
    """

    def setUp(self):
        # get current script directory path. We are in /an/unknown/path/odie/core/tests
        cur_script_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # get parent dir. Now we are in /an/unknown/path/odie
        root_dir = os.path.normpath(cur_script_directory + os.sep + os.pardir)

        # get the action dir
        self.actions_dir = os.path.normpath(root_dir + os.sep + "odie/actions")

        # get stt dir
        self.stt_dir = os.path.normpath(root_dir + os.sep + "odie/stt")

        # get tts dir
        self.tts_dir = os.path.normpath(root_dir + os.sep + "odie/tts")

        # get wakeon dir
        self.wakeon_dir = os.path.normpath(root_dir + os.sep + "odie/wakeon")
        # skip composite actions
        self.action_to_skip = ['alphabot', 'ultrasonic_ranging', 'trsensors', 'servo']

    def test_packages_present(self):
        """
        Check that the actions folder exist in the root of the project
        """
        self.assertTrue(os.path.isdir(self.actions_dir))
        self.assertTrue(os.path.isdir(self.stt_dir))
        self.assertTrue(os.path.isdir(self.tts_dir))
        self.assertTrue(os.path.isdir(self.wakeon_dir))

    def test_can_import_actions(self):
        """
        Try to import each actions that are present in the actions package
        :return:
        """
        actions = self.get_package_in_folder(self.actions_dir)
        package_name = "actions"
        for action_name in actions:
            if action_name not in self.action_to_skip:
                module_name = action_name.capitalize()
                self.dynamic_import(package_name, module_name)

    def test_can_import_stt(self):
        """
        Try to import each stt that are present in the stt package
        :return:
        """
        stts = self.get_package_in_folder(self.stt_dir)
        package_name = "stt"
        for stt_name in stts:
            module_name = stt_name.capitalize()
            self.dynamic_import(package_name, module_name)

    def test_can_import_tts(self):
        """
        Try to import each tts that are present in the tts package
        :return:
        """
        ttss = self.get_package_in_folder(self.tts_dir)
        package_name = "tts"
        for tts_name in ttss:
            module_name = tts_name.capitalize()
            self.dynamic_import(package_name, module_name)

    def test_can_import_wakeon(self):
        """
        Try to import each wakeon that are present in the wakeon package
        :return:
        """
        wakeons = self.get_package_in_folder(self.wakeon_dir)
        package_name = "wakeon"
        for wakeon in wakeons:
            module_name = wakeon.capitalize()
            self.dynamic_import(package_name, module_name)

    @staticmethod
    def get_package_in_folder(folder):
        """
        receive a path in <folder>, return a list of package in that folder.
        The function test if elements in that path are directory and return a list of those directory
        :param folder: Path of a folder to return package
        :return: list of package name
        """
        # get the list of actions in the actions packages
        el_folder = os.listdir(folder)
        # we keep only package. Because we have _init_.py or other stuff in what listdir returned
        packages_in_folder = list()
        for el in el_folder:
            if os.path.isdir(folder + os.sep + el) and not '__pycache__' in el:
                packages_in_folder.append(el)
        return packages_in_folder

    def dynamic_import(self, package_name, module_name):
        """
        Dynamic import of a module by its name.
        package name can be:
        - wakeons
        - actions
        - stt
        - tts
        :param package_name: name of the mother package
        :param module_name: module name to load
        :return:
        """
        module_name_with_path = "odie." + package_name + "." + module_name.lower() + "." + module_name.lower()
        mod = __import__(module_name_with_path, fromlist=[module_name])
        try:
            getattr(mod, module_name)
        except AttributeError:
            self.fail("The module %s does not exist in package %s" % (module_name, package_name))


if __name__ == '__main__':
    unittest.main()

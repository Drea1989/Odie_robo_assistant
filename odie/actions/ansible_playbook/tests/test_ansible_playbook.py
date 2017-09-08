import os
import unittest
from collections import namedtuple

import mock

from odie.actions.ansible_playbook import Ansible_playbook
from odie.core.ActionModule import MissingParameterException


class TestAnsible_Playbook(unittest.TestCase):

    def setUp(self):
        self.task_file = "task_file"
        self.random = "random"
        self.test_file = "/tmp/odie_text_ansible_playbook.txt"

    def testParameters(self):
        def run_test(parameters_to_test):
            with self.assertRaises(MissingParameterException):
                Ansible_playbook(**parameters_to_test)

        # empty
        parameters = dict()
        run_test(parameters)

        # missing task_file
        parameters = {
            "random": self.random
        }
        run_test(parameters)

        # missing sudo user
        parameters = {
            "sudo": True,
            "random": self.random
        }
        run_test(parameters)

        # missing sudo password
        parameters = {
            "sudo": True,
            "sudo_user": "user"
        }
        run_test(parameters)

        # parameters ok
        parameters = {
            "task_file": "odie/actions/ansible_playbook/tests/test_ansible_playbook_action.yml",
            "sudo": True,
            "sudo_user": "user",
            "sudo_password": "password"
        }

        with mock.patch("ansible.executor.playbook_executor.PlaybookExecutor.run"):
            instanciated_action = Ansible_playbook(**parameters)
            self.assertTrue(instanciated_action._is_parameters_ok)

    def test_create_file_via_ansible_playbook(self):
        """
        This test will use an ansible playbook the create a file. We check that the file has been created
        """
        # without sudo
        param = {
            "task_file": "odie/actions/ansible_playbook/tests/test_ansible_playbook_action.yml"
        }

        Ansible_playbook(**param)

        self.assertTrue(os.path.isfile(self.test_file))

        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        # with sudo
        param = {
            "task_file": "odie/actions/ansible_playbook/tests/test_ansible_playbook_action.yml",
            "sudo": True,
            "sudo_user": "user",
            "sudo_password": "password"
        }

        Options = namedtuple('Options',
                             ['connection', 'forks', 'become', 'become_method', 'become_user', 'check', 'listhosts',
                              'listtasks', 'listtags', 'syntax', 'module_path'])

        expected_option = Options(connection='local', forks=100, become=True, become_method="sudo",
                                  become_user="user", check=False, listhosts=False, listtasks=False, listtags=False,
                                  syntax=False, module_path="")

        with mock.patch("ansible.executor.playbook_executor.PlaybookExecutor.run") as playbookExecutor:
            instance_action = Ansible_playbook(**param)
            playbookExecutor.assert_called_once()

            self.assertEqual(instance_action._get_options(), expected_option)


if __name__ == '__main__':
    unittest.main()

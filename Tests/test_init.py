import unittest

import logging

import sys

import mock

from odie import parse_args, configure_logging, main


class TestInit(unittest.TestCase):

    def test_parse_args(self):
        # start option
        parser = parse_args(['value'])
        self.assertEqual(parser.action, "value")

        # no option
        with self.assertRaises(SystemExit):
            parse_args([])

        parser = parse_args(['start', '--run-neuron', 'run_neuron'])
        self.assertEqual(parser.run_neuron, 'run_neuron')

        parser = parse_args(['start', '--run-order', 'my order'])
        self.assertEqual(parser.run_order, 'my order')

    def test_configure_logging(self):
        logger = logging.getLogger("odie")
        # Level 10 = DEBUG
        configure_logging(debug=True)
        self.assertEqual(logger.getEffectiveLevel(), 10)
        logger.propagate = False

        # Level 20 = INFO
        configure_logging(debug=False)
        self.assertEqual(logger.getEffectiveLevel(), 20)

        # disable after testing
        logger.disabled = True

    def test_main(self):
        # test start odie
        sys.argv = ['odie.py', 'start']
        with mock.patch('odie.start_rest_api') as mock_rest_api:
            with mock.patch('odie.start_odie') as mock_start_odie:
                mock_rest_api.return_value = None
                main()
                mock_rest_api.assert_called()
                mock_start_odie.assert_called()
            mock_rest_api.return_value = None
            main()
            mock_rest_api.assert_called()

        # test start gui
        sys.argv = ['odie.py', 'gui']
        with mock.patch('odie.core.ShellGui.__init__') as mock_shell_gui:
            mock_shell_gui.return_value = None
            main()
            mock_shell_gui.assert_called()

        # test run_neuron
        sys.argv = ['odie.py', 'start', '--run-neuron', 'neuron_name']
        with mock.patch('odie.core.NeuronLauncher.start_neuron_by_name') as mock_neuron_launcher:
            mock_neuron_launcher.return_value = None
            main()
            mock_neuron_launcher.assert_called()

        # test run order
        sys.argv = ['odie.py', 'start', '--run-order', 'my order']
        with mock.patch('odie.core.NeuronLauncher.run_matching_neuron_from_order') as mock_neuron_launcher:
            mock_neuron_launcher.return_value = None
            main()
            mock_neuron_launcher.assert_called()

        # action doesn't exist
        sys.argv = ['odie.py', 'non_existing_action']
        with self.assertRaises(SystemExit):
            main()

        # install
        sys.argv = ['odie.py', 'install', '--git-url', 'https://my_url']
        with mock.patch('odie.core.ResourcesManager.install') as mock_resource_manager:
            mock_resource_manager.return_value = None
            main()
            mock_resource_manager.assert_called()

        # install, no URL
        sys.argv = ['odie.py', 'install']
        with self.assertRaises(SystemExit):
            main()

        sys.argv = ['odie.py', 'install', '--git-url']
        with self.assertRaises(SystemExit):
            main()

        # uninstall
        sys.argv = ['odie.py', 'uninstall', '--action-name', 'action_name']
        with mock.patch('odie.core.ResourcesManager.uninstall') as mock_resource_manager:
            mock_resource_manager.return_value = None
            main()
            mock_resource_manager.assert_called()

        sys.argv = ['odie.py', 'uninstall']
        with self.assertRaises(SystemExit):
            main()


if __name__ == '__main__':
    unittest.main()

    # suite = unittest.TestSuite()
    # suite.addTest(TestInit("test_main"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)

from odie.core.ConfigurationManager.ConfigurationChecker import ConfigurationChecker
if ConfigurationChecker().check_platform():
    from .read_line import Read_line
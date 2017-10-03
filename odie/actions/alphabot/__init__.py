from odie.core.ConfigurationManager.ConfigurationChecker import ConfigurationChecker
if ConfigurationChecker().check_platform():
    from .setrover import Setrover
    from .initialiserover import Initialiserover

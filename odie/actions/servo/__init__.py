from odie.core.ConfigurationManager.ConfigurationChecker import ConfigurationChecker
if ConfigurationChecker().check_platform():
    from .movecommand import Movecommand
    from .initialiseservo import Initialiseservo

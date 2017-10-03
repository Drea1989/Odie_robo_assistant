from odie.core.ConfigurationManager.ConfigurationChecker import ConfigurationChecker
if ConfigurationChecker().check_platform():
    from .ultrasonic_reading import Ultrasonic_dist

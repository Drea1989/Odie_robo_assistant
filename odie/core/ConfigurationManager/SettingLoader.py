import logging
import os
from six import with_metaclass

from odie.core.Models.RpiSettings import RpiSettings
from .YAMLLoader import YAMLLoader
from odie.core.Models.Resources import Resources
from odie.core.Models.Postgres import Postgres
from odie.core.Models.Cloud import Cloud
from odie.core.Models.RecognitionOptions import RecognitionOptions
from odie.core.Utils.Utils import Utils
from odie.core.Models import Singleton
from odie.core.Models.RestAPI import RestAPI
from odie.core.Models.Settings import Settings
from odie.core.Models.Stt import Stt
from odie.core.Models.Wakeon import Wakeon
from odie.core.Models.Player import Player
from odie.core.Models.Tts import Tts
from odie.core.Utils.FileManager import FileManager

FILE_NAME = "settings.yml"

logging.basicConfig()
logger = logging.getLogger("odie")


class SettingInvalidException(Exception):
    """
    Some data must match the expected value/type

    .. seealso:: Settings
    """
    pass


class NullSettingException(Exception):
    """
    Some Attributes can not be Null

    .. seealso:: Settings
    """
    pass


class SettingNotFound(Exception):
    """
    Some Attributes are missing

    .. seealso:: Settings
    """
    pass


class SettingLoader(with_metaclass(Singleton, object)):
    """
    This Class is used to get the Settings YAML and the Settings as an object
    """

    def __init__(self, file_path=None):
        self.file_path = file_path
        if self.file_path is None:
            self.file_path = Utils.get_real_file_path(FILE_NAME)
        else:
            self.file_path = Utils.get_real_file_path(file_path)
        # if the returned file path is none, the file doesn't exist
        if self.file_path is None:
            raise SettingNotFound("Settings.yml file not found")
        self.yaml_config = self._get_yaml_config()
        self.settings = self._get_settings()

    def _get_yaml_config(self):
        """
        Class Methods which loads default or the provided YAML file and return it as a String

        :return: The loaded settings YAML
        :rtype: dict

        :Example:
            settings_yaml = SettingLoader.get_yaml_config(/var/tmp/settings.yml)

        .. warnings:: Class Method
        """
        return YAMLLoader.get_config(self.file_path)

    def _get_settings(self):
        """
        Class Methods which loads default or the provided YAML file and return a Settings Object

        :return: The loaded Settings
        :rtype: Settings

        :Example:

            settings = SettingLoader.get_settings(file_path="/var/tmp/settings.yml")

        .. seealso:: Settings
        .. warnings:: Class Method
        """

        # create a new setting
        setting_object = Settings()

        # Get the setting parameters
        settings = self._get_yaml_config()
        default_stt_name = self._get_default_speech_to_text(settings)
        default_tts_name = self._get_default_text_to_speech(settings)
        default_wakeon_name = self._get_default_wakeon(settings)
        default_player_name = self._get_default_player(settings)
        stts = self._get_stts(settings)
        ttss = self._get_ttss(settings)
        wakeons = self._get_wakeons(settings)
        players = self._get_players(settings)
        random_wake_up_answers = self._get_random_wake_up_answers(settings)
        random_wake_up_sound = self._get_random_wake_up_sounds(settings)
        play_on_ready_notification = self._get_play_on_ready_notification(settings)
        on_ready_answers = self._get_on_ready_answers(settings)
        on_ready_sounds = self._get_on_ready_sounds(settings)
        rest_api = self._get_rest_api(settings)
        cache_path = self._get_cache_path(settings)
        default_neuron = self._get_default_neuron(settings)
        resources = self._get_resources(settings)
        variables = self._get_variables(settings)
        rpi_settings = self._get_rpi_settings(settings)
        postgres = self._get_postgres(settings)
        alphabot = self._get_alphabot(settings)
        cloud = self._get_cloud(settings)
        recognition_options = self._get_recognition_options(settings)

        # Load the setting singleton with the parameters
        setting_object.default_tts_name = default_tts_name
        setting_object.default_stt_name = default_stt_name
        setting_object.default_wakeon_name = default_wakeon_name
        setting_object.default_player_name = default_player_name
        setting_object.stts = stts
        setting_object.ttss = ttss
        setting_object.wakeons = wakeons
        setting_object.players = players
        setting_object.random_wake_up_answers = random_wake_up_answers
        setting_object.random_wake_up_sounds = random_wake_up_sound
        setting_object.play_on_ready_notification = play_on_ready_notification
        setting_object.on_ready_answers = on_ready_answers
        setting_object.on_ready_sounds = on_ready_sounds
        setting_object.rest_api = rest_api
        setting_object.cache_path = cache_path
        setting_object.default_neuron = default_neuron
        setting_object.resources = resources
        setting_object.variables = variables
        setting_object.rpi_settings = rpi_settings
        setting_object.postgres = postgres
        setting_object.alphabot = alphabot
        setting_object.cloud = cloud
        setting_object.recognition_options = recognition_options

        return setting_object

    @staticmethod
    def _get_default_speech_to_text(settings):
        """
        Get the default speech to text defined in the settings.yml file

        :param settings: The YAML settings file
        :type settings: dict
        :return: the default speech to text
        :rtype: str

        :Example:

            default_stt_name = cls._get_default_speech_to_text(settings)

        .. seealso:: Stt
        .. raises:: NullSettingException, SettingNotFound
        .. warnings:: Static and Private
        """

        try:
            default_speech_to_text = settings["default_speech_to_text"]
            if default_speech_to_text is None:
                raise NullSettingException("Attribute default_speech_to_text is null")
            logger.debug("Default STT: %s" % default_speech_to_text)
            return default_speech_to_text
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

    @staticmethod
    def _get_default_text_to_speech(settings):
        """
        Get the default text to speech defined in the settings.yml file

        :param settings: The YAML settings file
        :type settings: dict
        :return: the default text to speech
        :rtype: str

        :Example:

            default_tts_name = cls._get_default_text_to_speech(settings)

        .. seealso:: Tts
        .. raises:: NullSettingException, SettingNotFound
        .. warnings:: Static and Private
        """

        try:
            default_text_to_speech = settings["default_text_to_speech"]
            if default_text_to_speech is None:
                raise NullSettingException("Attribute default_text_to_speech is null")
            logger.debug("Default TTS: %s" % default_text_to_speech)
            return default_text_to_speech
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

    @staticmethod
    def _get_default_wakeon(settings):
        """
        Get the default wakeon defined in the settings.yml file
        :param settings: The YAML settings file
        :type settings: dict
        :return: the default wakeon
        :rtype: str

        :Example:

            default_wakeon_name = cls._get_default_wakeon(settings)

        .. seealso:: wakeon
        .. raises:: NullSettingException, SettingNotFound
        .. warnings:: Static and Private
        """

        try:
            default_wakeon = settings["default_wakeon"]
            if default_wakeon is None:
                raise NullSettingException("Attribute default_wakeon is null")
            logger.debug("Default wakeon name: %s" % default_wakeon)
            return default_wakeon
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

    @staticmethod
    def _get_default_player(settings):
        """
        Get the default player defined in the settings.yml file
        :param settings: The YAML settings file
        :type settings: dict
        :return: the default player
        :rtype: str

        :Example:

            default_player_name = cls._get_default_player(settings)

        .. seealso:: Player
        .. raises:: NullSettingException, SettingNotFound
        .. warnings:: Static and Private
        """

        try:
            default_player = settings["default_player"]
            if default_player is None:
                raise NullSettingException("Attribute default_player is null")
            logger.debug("Default Player name: %s" % default_player)
            return default_player
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

    @staticmethod
    def _get_stts(settings):
        """
        Return a list of stt object

        :param settings: The YAML settings file
        :type settings: dict
        :return: List of Stt
        :rtype: list

        :Example:

            stts = cls._get_stts(settings)

        .. seealso:: Stt
        .. raises:: SettingNotFound
        .. warnings:: Static Method and Private
        """

        try:
            speechs_to_text_list = settings["speech_to_text"]
        except KeyError:
            raise SettingNotFound("speech_to_text settings not found")

        stts = list()
        for speechs_to_text_el in speechs_to_text_list:
            if isinstance(speechs_to_text_el, dict):
                for stt_name in speechs_to_text_el:
                    name = stt_name
                    parameters = speechs_to_text_el[name]
                    new_stt = Stt(name=name, parameters=parameters)
                    stts.append(new_stt)
            else:
                # the stt does not have parameter
                new_stt = Stt(name=speechs_to_text_el, parameters=dict())
                stts.append(new_stt)
        return stts

    @staticmethod
    def _get_ttss(settings):
        """

        Return a list of stt object

        :param settings: The YAML settings file
        :type settings: dict
        :return: List of Ttss
        :rtype: list

        :Example:

            ttss = cls._get_ttss(settings)

        .. seealso:: Tts
        .. raises:: SettingNotFound
        .. warnings:: Static Method and Private
        """

        try:
            text_to_speech_list = settings["text_to_speech"]
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

        ttss = list()
        for text_to_speech_el in text_to_speech_list:
            if isinstance(text_to_speech_el, dict):
                for tts_name in text_to_speech_el:
                    name = tts_name
                    parameters = text_to_speech_el[name]
                    new_tts = Tts(name=name, parameters=parameters)
                    ttss.append(new_tts)
            else:
                # the action does not have parameter
                new_tts = Tts(name=text_to_speech_el)
                ttss.append(new_tts)
        return ttss

    @staticmethod
    def _get_wakeons(settings):
        """
        Return a list of Wakeon object

        :param settings: The YAML settings file
        :type settings: dict
        :return: List of Wakeon
        :rtype: list

        :Example:

            wakeons = cls._get_wakeons(settings)

        .. seealso:: Wakeon
        .. raises:: SettingNotFound
        .. warnings:: Static Method and Private
        """

        try:
            wakeons_list = settings["wakeons"]
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

        wakeons = list()
        for wakeon_el in wakeons_list:
            if isinstance(wakeon_el, dict):
                for wakeon_name in wakeon_el:
                    name = wakeon_name
                    parameters = wakeon_el[name]
                    new_wakeon = Wakeon(name=name, parameters=parameters)
                    wakeons.append(new_wakeon)
            else:
                # the action does not have parameter
                new_wakeon = Wakeon(name=wakeon_el)
                wakeons.append(new_wakeon)
        return wakeons

    @staticmethod
    def _get_players(settings):
        """
        Return a list of Player object

        :param settings: The YAML settings file
        :type settings: dict
        :return: List of Player
        :rtype: list

        :Example:

            players = cls._get_players(settings)

        .. seealso:: players
        .. raises:: SettingNotFound
        .. warnings:: Static Method and Private
        """

        try:
            players_list = settings["players"]
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

        players = list()
        for player_el in players_list:
            if isinstance(player_el, dict):
                for player_name in player_el:
                    name = player_name
                    parameters = player_el[name]
                    new_player = Player(name=name, parameters=parameters)
                    players.append(new_player)
            else:
                # the player does not have parameters
                new_player = Player(name=player_el)
                players.append(new_player)
        return players

    @staticmethod
    def _get_random_wake_up_answers(settings):
        """
        Return a list of the wake up answers set up on the settings.yml file

        :param settings: The YAML settings file
        :type settings: dict
        :return: List of wake up answers
        :rtype: list of str

        :Example:

            wakeup = cls._get_random_wake_up_answers(settings)

        .. seealso::
        .. raises:: NullSettingException
        .. warnings:: Class Method and Private
        """

        try:
            random_wake_up_answers_list = settings["random_wake_up_answers"]
        except KeyError:
            # User does not provide this settings
            return None

        # The list cannot be empty
        if random_wake_up_answers_list is None:
            raise NullSettingException("random_wake_up_answers settings is null")

        return random_wake_up_answers_list

    @staticmethod
    def _get_random_wake_up_sounds(settings):
        """
        Return a list of the wake up sounds set up on the settings.yml file

        :param settings: The YAML settings file
        :type settings: dict
        :return: list of wake up sounds
        :rtype: list of str

        :Example:

            wakeup_sounds = cls._get_random_wake_up_sounds(settings)

        .. seealso::
        .. raises:: NullSettingException
        .. warnings:: Class Method and Private
        """

        try:
            random_wake_up_sounds_list = settings["random_wake_up_sounds"]
            # In case files are declared in settings.yml, make sure odie can access them.
            for sound in random_wake_up_sounds_list:
                if Utils.get_real_file_path(sound) is None:
                    raise SettingInvalidException("sound file %s not found" % sound)
        except KeyError:
            # User does not provide this settings
            return None

        # The the setting is present, the list cannot be empty
        if random_wake_up_sounds_list is None:
            raise NullSettingException("random_wake_up_sounds settings is empty")

        return random_wake_up_sounds_list

    @staticmethod
    def _get_rest_api(settings):
        """
        Return the settings of the RestApi

        :param settings: The YAML settings file
        :type settings: dict
        :return: the RestApi object
        :rtype: RestApi

        :Example:

            rest_api = cls._get_rest_api(settings)

        .. seealso:: RestApi
        .. raises:: SettingNotFound, NullSettingException, SettingInvalidException
        .. warnings:: Class Method and Private
        """

        try:
            rest_api = settings["rest_api"]
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

        if rest_api is not None:
            try:
                password_protected = rest_api["password_protected"]
                if password_protected is None:
                    raise NullSettingException("password_protected setting cannot be null")
                login = rest_api["login"]
                password = rest_api["password"]
                if password_protected:
                    if login is None:
                        raise NullSettingException("login setting cannot be null if password_protected is True")
                    if password is None:
                        raise NullSettingException("password setting cannot be null if password_protected is True")
                active = rest_api["active"]
                if active is None:
                    raise NullSettingException("active setting cannot be null")
                port = rest_api["port"]
                if port is None:
                    raise NullSettingException("port setting cannot be null")
                # check that the port in an integer
                try:
                    port = int(port)
                except ValueError:
                    raise SettingInvalidException("port must be an integer")
                # check the port is a valid port number
                if not 1024 <= port <= 65535:
                    raise SettingInvalidException("port must be in range 1024-65535")

                # check the CORS request settings
                allowed_cors_origin = False
                if "allowed_cors_origin" in rest_api:
                    allowed_cors_origin = rest_api["allowed_cors_origin"]

            except KeyError as e:
                raise SettingNotFound("%s settings not found" % e)

            # config ok, we can return the rest api object
            rest_api_obj = RestAPI(password_protected=password_protected, login=login, password=password,
                                   active=active, port=port, allowed_cors_origin=allowed_cors_origin)
            return rest_api_obj
        else:
            raise NullSettingException("rest_api settings cannot be null")

    @staticmethod
    def _get_cache_path(settings):
        """
        Return the path where to store the cache

        :param settings: The YAML settings file
        :type settings: dict
        :return: the path to store the cache
        :rtype: String

        :Example:

            cache_path = cls._get_cache_path(settings)

        .. seealso::
        .. raises:: SettingNotFound, NullSettingException, SettingInvalidException
        .. warnings:: Class Method and Private
        """

        try:
            cache_path = settings["cache_path"]
        except KeyError as e:
            raise SettingNotFound("%s setting not found" % e)

        if cache_path is None:
            raise NullSettingException("cache_path setting cannot be null")

        # test if that path is usable
        if FileManager.is_path_exists_or_creatable(cache_path):
            return cache_path
        else:
            raise SettingInvalidException("The cache_path seems to be invalid: %s" % cache_path)

    @staticmethod
    def _get_default_neuron(settings):
        """
        Return the name of the default neuron

        :param settings: The YAML settings file
        :type settings: dict
        :return: the default neuron name
        :rtype: String

        :Example:

            default_neuron = cls._get_default_neuron(settings)

        .. seealso::
        .. raises:: SettingNotFound, NullSettingException, SettingInvalidException
        .. warnings:: Class Method and Private
        """

        try:
            default_neuron = settings["default_neuron"]
            logger.debug("Default neuron: %s" % default_neuron)
        except KeyError:
            default_neuron = None

        return default_neuron

    @staticmethod
    def _get_resources(settings):
        """
        Return a resources object that contains path of third party modules

        :param settings: The YAML settings file
        :type settings: dict
        :return: the resource object
        :rtype: Resources

        :Example:

            resource_directory = cls._get_resource_dir(settings)

        .. seealso::
        .. raises:: SettingNotFound, NullSettingException, SettingInvalidException
        .. warnings:: Class Method and Private
        """
        # return an empty resource object anyway
        resource_object = Resources()
        try:
            resource_dir = settings["resource_directory"]
            logger.debug("Resource directory neuron: %s" % resource_dir)

            action_folder = None
            stt_folder = None
            tts_folder = None
            wakeon_folder = None
            cue_folder = None

            if "action" in resource_dir:
                action_folder = resource_dir["action"]
                if os.path.exists(action_folder):
                    logger.debug("[SettingLoader] Action resource folder path loaded: %s" % action_folder)
                    resource_object.action_folder = action_folder
                else:
                    raise SettingInvalidException("The path %s does not exist on the system" % action_folder)

            if "stt" in resource_dir:
                stt_folder = resource_dir["stt"]
                if os.path.exists(stt_folder):
                    logger.debug("[SettingLoader] stt resource folder path loaded: %s" % stt_folder)
                    resource_object.stt_folder = stt_folder
                else:
                    raise SettingInvalidException("The path %s does not exist on the system" % stt_folder)

            if "tts" in resource_dir:
                tts_folder = resource_dir["tts"]
                if os.path.exists(tts_folder):
                    logger.debug("[SettingLoader] tts resource folder path loaded: %s" % tts_folder)
                    resource_object.tts_folder = tts_folder
                else:
                    raise SettingInvalidException("The path %s does not exist on the system" % tts_folder)

            if "wakeon" in resource_dir:
                wakeon_folder = resource_dir["wakeon"]
                if os.path.exists(wakeon_folder):
                    logger.debug("[SettingLoader] Wakeon resource folder path loaded: %s" % wakeon_folder)
                    resource_object.wakeon_folder = wakeon_folder
                else:
                    raise SettingInvalidException("The path %s does not exist on the system" % wakeon_folder)

            if "cue" in resource_dir:
                cue_folder = resource_dir["cue"]
                if os.path.exists(cue_folder):
                    logger.debug("[SettingLoader] Cue resource folder path loaded: %s" % cue_folder)
                    resource_object.cue_folder = cue_folder
                else:
                    raise SettingInvalidException("The path %s does not exist on the system" % cue_folder)

            resource_object = Resources(action_folder=action_folder,
                                        stt_folder=stt_folder,
                                        tts_folder=tts_folder,
                                        wakeon_folder=wakeon_folder,
                                        cue_folder=cue_folder)
        except KeyError:
            logger.debug("Resource directory not found in settings")

        return resource_object

    @staticmethod
    def _get_play_on_ready_notification(settings):
        """
        Return the on_ready_notification setting. If the user didn't provided it the default is never
        :param settings: The YAML settings file
        :type settings: dict
        :return:
        """
        try:
            play_on_ready_notification = settings["play_on_ready_notification"]
        except KeyError:
            # User does not provide this settings, by default we set it to never
            play_on_ready_notification = "never"
            return play_on_ready_notification
        return play_on_ready_notification

    @staticmethod
    def _get_on_ready_answers(settings):
        """
        Return the list of on_ready_answers string from the settings.
        :param settings: The YAML settings file
        :type settings: dict
        :return: String parameter on_ready_answers
        """
        try:
            on_ready_answers = settings["on_ready_answers"]
        except KeyError:
            # User does not provide this settings
            return None

        return on_ready_answers

    @staticmethod
    def _get_on_ready_sounds(settings):
        """
        Return the list of on_ready_sounds string from the settings.
        :param settings: The YAML settings file
        :type settings: dict
        :return: String parameter on_ready_sounds
        """
        try:
            on_ready_sounds = settings["on_ready_sounds"]
            # In case files are declared in settings.yml, make sure odie can access them.
            for sound in on_ready_sounds:
                if Utils.get_real_file_path(sound) is None:
                    raise SettingInvalidException("sound file %s not found" % sound)
        except KeyError:
            # User does not provide this settings
            return None

        return on_ready_sounds

    @staticmethod
    def _get_variables(settings):
        """
        Return the dict of variables from the settings.
        :param settings: The YAML settings file
        :return: dict
        """

        variables = dict()
        try:
            variables_files_name = settings["var_files"]
            # In case files are declared in settings.yml, make sure odie can access them.
            for files in variables_files_name:
                var = Utils.get_real_file_path(files)
                if var is None:
                    raise SettingInvalidException("Variables file %s not found" % files)
                else:
                    variables.update(YAMLLoader.get_config(var))
            return variables
        except KeyError:
            # User does not provide this settings
            return dict()

    @staticmethod
    def _get_rpi_settings(settings):
        """
        return RpiSettings object
        :param settings: The loaded YAML settings file
        :return: 
        """

        try:
            rpi_settings_dict = settings["rpi"]
            rpi_settings = RpiSettings()
            # affect pin if there are declared
            if "pin_mute_button" in rpi_settings_dict:
                rpi_settings.pin_mute_button = rpi_settings_dict["pin_mute_button"]
            if "pin_led_started" in rpi_settings_dict:
                rpi_settings.pin_led_started = rpi_settings_dict["pin_led_started"]
            if "pin_led_muted" in rpi_settings_dict:
                rpi_settings.pin_led_muted = rpi_settings_dict["pin_led_muted"]
            if "pin_led_talking" in rpi_settings_dict:
                rpi_settings.pin_led_talking = rpi_settings_dict["pin_led_talking"]
            if "pin_led_listening" in rpi_settings_dict:
                rpi_settings.pin_led_listening = rpi_settings_dict["pin_led_listening"]

            return rpi_settings
        except KeyError:
            logger.debug("[SettingsLoader] No Rpi config")
            return None

    @staticmethod
    def _get_postgres(settings):
        """
        Return the dict of postgres from the settings.
        :param settings: The YAML settings file
        :return: dict
        """
        try:
            pg = settings["postgres"]

            if "host" in pg:
                host = pg["host"]

            if "port" in pg:
                port = pg["port"]

            if "database" in pg:
                database = pg["database"]

            if "user" in pg:
                user = pg["user"]

            if "password" in pg:
                password = pg["password"]

            if host is None \
                    and port is None \
                    and database is None \
                    and user is None \
                    and password is None:
                raise SettingInvalidException("Define : \'host\' or/and \'port\' or/and \'database\' or/and \'user\' or/and \'password\'")

            postgres = Postgres(host=host,
                                port=port,
                                database=database,
                                user=user,
                                password=password)
        except KeyError:
            logger.debug("Postgres not found in settings")
            postgres = None

        return postgres

    @staticmethod
    def _get_alphabot(settings):
        """
        Return the dict of _alphabot from the settings.
        :param settings: The YAML settings file
        :return: dict
        """
        alphabot = dict()
        try:
            alphabot = settings["alphabot"]
            return alphabot
        except KeyError:
            # User does not provide this settings
            return dict()

    @staticmethod
    def _get_cloud(settings):
        """
        Return the dict of cloud models from the settings.
        :param settings: The YAML settings file
        :return: dict
        """
        cl = list()
        try:
            clCategory = settings["cloud"]
        except KeyError:
            logger.debug("cloud settings not found")
            return cl

        for clSetting in clCategory:
            if isinstance(clSetting, dict):
                for category in clSetting:
                    name = category
                    parameters = clSetting[category]
                    new_cl = Cloud(category=name, parameters=parameters)
                    logger.debug('cloud object: {}'.format(new_cl))
                    cl.append(new_cl)
            else:
                # wrong config file
                logger.debug("cloud settings is invalid at: {}".format(clSetting))
        return cl

    @staticmethod
    def _get_recognition_options(settings):
        """
        return the value of stt_threshold
        :param settings: The loaded YAML settings file
        :return: integer or 1200 by default if not set
        """
        recognition_options = RecognitionOptions()

        try:
            recognition_options_dict = settings["RecognitionOptions"]

            if "energy_threshold" in recognition_options_dict:
                recognition_options.energy_threshold = recognition_options_dict["energy_threshold"]
                logger.debug("[SettingsLoader] energy_threshold set to %s" % recognition_options.energy_threshold)
            if "adjust_for_ambient_noise_second" in recognition_options_dict:
                recognition_options.adjust_for_ambient_noise_second = recognition_options_dict["adjust_for_ambient_noise_second"]
                logger.debug("[SettingsLoader] adjust_for_ambient_noise_second set to %s"
                             % recognition_options.adjust_for_ambient_noise_second)
            return recognition_options

        except KeyError:
            logger.debug("[SettingsLoader] no recognition_options defined. Set to default")

        logger.debug("[SettingsLoader] recognition_options: %s" % str(recognition_options))
        return recognition_options

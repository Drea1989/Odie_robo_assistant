import time
import six

from odie.core.ActionModule import ActionModule,  MissingParameterException


class Model(ActionModule):
    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)
        self.path = kwargs.get('path', None)
        self.platform = kwargs.get('platform', None)

        # check parameters
        if self._is_parameters_ok():
            if self.platform == 'neon':
                from neon.models import Model

                return Model(self.path)

            elif self.platform == 'tensorflow':

            return self.path
    

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the action
        :return: true if parameters are ok, raise an exception otherwise

        .. raises:: MissingParameterException
        """
        if self.path is None:
            raise MissingParameterException("You must set a model")
        return True

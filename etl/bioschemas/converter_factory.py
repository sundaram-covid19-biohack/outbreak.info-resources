import logging
from singleton_decorator import singleton

from etl.bioschemas.converter import Converter
from etl.protocols_io.bioschemas.converter import Converter as ProtocolsIOConverter
from etl.nature_protocols.bioschemas.converter import Converter as NatureProtocolsConverter


DEFAULT_VERBOSE = False


@singleton
class Factory():
    """Factory class for creating converters
    """
    def __init__(self, **kwargs):
        """
        """
        if 'verbose' in kwargs:
            self._verbose = kwargs['verbose']
        else:
            self._verbose = DEFAULT_VERBOSE

        if 'outdir' in kwargs:
            self._outdir = kwargs['outdir']

        if 'type' in kwargs:
            self._converter_type= kwargs['type']

    def create(self, converter_type: str = None) -> Converter:
        """Instantiate a converter based on the type
        :param converter_type: {str}
        """
        if converter_type is None:
            if self._converter_type is None:
                logging.error("converter_type is not defined")
                sys.exit(1)
            converter_type = self._converter_type

        if converter_type == 'protocols-io':
            converter = ProtocolsIOConverter(outdir=self._outdir, verbose=self._verbose)
        elif converter_type == 'nature-protocols':
            converter = NatureProtocolsConverter(outdir=self._outdir, verbose=self._verbose)
        else:
            logging.error("converter type '{}' is not supported".format(converter_type))
            sys.exit(1)
        return converter


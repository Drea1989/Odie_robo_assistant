import logging
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

logging.basicConfig()
logger = logging.getLogger("odie")


class PostgresManager(object):
    """
    Class used to manage PostgreSQL
    """
    def __init__(self):
        pass

    # @staticmethod
    def get_connection(host, database, user, password):
        """
        Create a connection object with PostgreSQL
        :param host: the PostgreSQL host address
        :type host: str
        :param database: the PostgreSQL database
        :type database: str
        :param user: the PostgreSQL user
        :type user: str
        :param password: the PostgreSQL password
        :type password: str
        """
        try:
            if logger.levelname == "DEBUG":
                return psycopg2.connect(host, database, user, password)
            else:
                return psycopg2.connect(host, database, user, password)
        except:
            logger.error("PostgreSQL Connection failed")

    # @staticmethod
    def create_engine(host='localhost', port=5432, database=None, user=None, password=None):
        """
        Create an sqlalchemy engine object
        :param host: the PostgreSQL host address
        :type host: str
        :param database: the PostgreSQL database
        :type database: str
        :param user: the PostgreSQL user
        :type user: str
        :param password: the PostgreSQL password
        :type password: str

        .. raises:: IOError
        """
        try:
            return create_engine('postgresql://'+user+':'+password+'@'+host+':'+str(port)+'/'+database)
        except:
            logger.error("PostgreSQL could not create an engine")

    def create_text_search_index(con=None):
        """
        this function create the full text search index to speed up the recovery of the neurons from the brain table
        """
        try:
            cur = con.cursor()
            cur.execute("CREATE INDEX order_idx ON brain USING GIN (to_tsvector('english', order));")
            return True
        except:
            logger.debug("postgresql failed to create index brain")
            return False

    def search_match_neuron(con=None, term=None):
        """
        this function use full text search to recover of the neurons from the brain table that matches the term
        """
        try:
            cur = con.cursor()
            # con.execute("SELECT name FROM brain
            #             WHERE to_tsvector('english', order) @@ to_tsquery('english', '{}')
            #             ORDER BY ts_rank_cd(to_tsvector('english', order), to_tsquery('english', '{}') )
            #             DESC LIMIT 1;".format(term))
            # testing simple execution
            con.execute("SELECT name, cues FROM brain WHERE to_tsvector('english', order) @@ to_tsquery('english', '{}')LIMIT 1;".format(term))
            return cur.fetchall()
        except:
            logger.debug("postgresql failed to retreive neuron from brain")
            return list()

    def save_brain_table(pg=None, brain=None):
        """
        function to create the brain table in postgres.
        if the table exists it gets dropped and recreated with the new brain.
        :param pg: the PostgreSQL settings
        :type pg: object
        :param brain: the brain to be saved
        :type brain: brain object
        """

        engine = PostgresManager.create_engine(pg.host, pg.port, pg.database, pg.user, pg.password)

        # name of postgres table and python dictionary
        try:
            logger.debug("[CreateBrainTable] begins with brain")
            braindict = {}
            neuron_names = []
            neuron_cues = []
            n_number = 0
            for neuron in brain.neurons:
                brain_insert = neuron.serialize()
                logger.debug("[CreateBrainTable] neuron serialized: {}".format(brain_insert))
                neuron_names.append(brain_insert['name'])
                logger.debug("[CreateBrainTable] name: {}".format(neuron_names))
                logger.debug("[CreateBrainTable] cues: {}".format(brain_insert['cues']))

                for cue in brain_insert['cues']:
                    for key in cue:
                        logger.debug("[CreateBrainTable] cue dict: {}, {}".format(key, cue[key]))
                        if key == 'order' or key == 'Order':
                            neuron_cues.append(cue[key])
                n_number += 1
            for neuron in range(n_number):
                braindict[neuron] = {'name': neuron_names[neuron], 'cue': neuron_cues[neuron]}
            logger.debug("[CreateBrainTable] this is the df brain: {} , {}".format(braindict.keys(), braindict.values()))
            dfLoad = pd.DataFrame.from_dict(braindict)
            logger.debug("[CreateBrainTable] df created: {}".format(dfLoad.head()))
            dfLoad.to_sql(name="brain", con=engine, if_exists="replace", index=False)
            con = PostgresManager.get_connection(pg.host, pg.database, pg.user, pg.password)
            idx_success = PostgresManager.create_text_search_index(con)
            if idx_success:
                return True
            else:
                return False
        except:
            logger.debug("postgresql failed to insert brain")
            return False

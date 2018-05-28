"""
Big Query CLient
"""
# connect
# insert
# disconnect
# reconnect
# status
import sys
import logging
# import json
# import time

from google.cloud import bigquery
# bigquery.__version__

from .. support.debug import pretty_error_str
logger = logging.getLogger('scraper_pipeline.bq_client')

# TODO: there is no need to pass logger as an argument. Can create global logger with same namespace.

# ##############################################################################
#                                  EXCEPTIONS
# ##############################################################################
from google.api_core.exceptions import ClientError as ClientError # 4XX errors
from google.api_core.exceptions import ServerError as ServerError # 5xx errors
from google.api_core.exceptions import TooManyRequests as TooManyRequestsError # 429 error
from google.api_core.exceptions import GatewayTimeout as ServerTimeoutError #504 server timeout


# ##############################################################################
#                                  BIG QUERY SUPPORT
# ##############################################################################
def connect_to_bigquery(credentials, gcp_project_id):
    try:
        logger.info("Connecting to big query")
        bqclient = bigquery.Client.from_service_account_json(credentials)
        bqclient.project = gcp_project_id # set the google coud project to connect to
        logger.debug("- done")
        return bqclient
    except Exception as e:
        # TODO: raise alarm if could not connect to BQ
        raise e

def get_bigquery_table(client, dataset_id, table_id, project_id=None):
    """ Optionally specify a project if dataset is not in same project as
        the one set in client
    """
    try:
        logger.info("Connecting to big query table")
        dataset_ref = client.dataset(dataset_id, project=project_id)
        table_ref = dataset_ref.table(table_id)
        table = client.get_table(table_ref)  # API Request
        logger.debug("- done")
        return table
    except:
        # TODO: raise alarm if could not connect to BQ
        logger.critical(pretty_error_str("Could not connect to BQ table"))
        raise




# ##############################################################################
#                                     DB_CLIENT
# ##############################################################################
class BQ_Client(object):
    """
    Args:
        credentials:  (str) path to json file with credentials
        dataset_id:   (str)
        table_id:     (str)
        google_project_id: (str)
    """
    def __init__(self, credentials, dataset_id, table_id, google_project_id):
        self.credentials = credentials
        self.google_project_id = google_project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = None
        self.table = None

    @property
    def is_connected(self):
        assert False, "TODO: `is_connected` not implemented yet"

    def parse_credentials(self, credentials):
        # For bigquery it takes the filepath to a json file directly
        self.credentials = credentials

    def connect(self, to_table=True):
        """
        to_table:   (bool) should it connect to table as well?
        """
        self.client = connect_to_bigquery(credentials=self.credentials,
                                       gcp_project_id=self.google_project_id)

        if to_table:
            # hacky if statement to make it backwards compatible
            self.table = get_bigquery_table(self.client,
                                        dataset_id=self.dataset_id,
                                       table_id=self.table_id,
                                       project_id=self.google_project_id)

    def connect_to_table(self, table_id=None):
        if table_id is not None:
            self.table_id = table_id

        self.table = get_bigquery_table(self.client,
                                    dataset_id=self.dataset_id,
                                    table_id=self.table_id,
                                    project_id=self.google_project_id)

    def create_table(self, table_id, schema):
        """ Creates a new table in Big Query"""
        dataset_ref = self.client.dataset(self.dataset_id)
        table_ref = dataset_ref.table(table_id)
        table = bigquery.Table(table_ref, schema=schema)
        table = self.client.create_table(table)

        assert table.table_id == table_id, "Something went wrong"
        return True

    def store(self, data):
        """ given a dictionary object, it pushes the data to database """
        # TODO: Maybe do multiple retries and timeouts when inserting.
        try:
            logger.debug("PASSING processed message to database (id={})".format(data.get("id", "")))
            errors = self.client.insert_rows(self.table, [data])
            assert errors == [], "Errors in inserting data: {}".format(str(errors))
            logger.debug("SUCCESS sending a message to database (id={})".format(data.get("id", "")))
        except:
            raise

    # Alias (for backwards comatibility)
    def insert(self, data):
        self.store(data)

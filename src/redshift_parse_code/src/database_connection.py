import os

import sqlalchemy as sql
import psycopg2

from datetime import datetime
from .queries import Queries


class DataBaseConnection:
    q = Queries()

    def __init__(self, s3=None, redshift=False):
        """
        Connects by default to local postgresql.
        """

        self.redshift = redshift
        self.s3 = s3
        if not redshift:
            self.engine = sql.create_engine('postgresql://postgres@localhost:5431/dev')
        else:
            ssl_bundle = os.path.abspath("{}/redshift-ca-bundle.crt".format(os.path.dirname(__file__)))
            self.engine = sql.create_engine(
                            os.environ.get('REDSHIFT_URI'),
                            connect_args={'sslrootcert': ssl_bundle,
                                          'sslmode': 'verify-ca'}
                          )

        self.connection = self.engine.connect()

    def build_db_if_needed(self):
        if not self.engine.dialect.has_table(self.engine, 'uploaded_files'):
            for query in self.q.get_build_queries(self.redshift)._asdict().values():
                self.connection.execute(query)

    def uploaded_files(self):
        result = self.safe_query(self.q.get_uploaded_files)
        return {(row['s3filename'], row['destination']) for row in result}

    def mark_uploaded(self, filename, destination):
        uploaded_at = datetime.now()
        self.safe_query(self.q.mark_uploaded.format(
                                    filename,
                                    destination,
                                    uploaded_at
                                )
                               )

    def load_csv(self, table, filename, csv_path, columns, region, iam_role):
        if self.redshift:
            self.connection.execute(self.q.get_load_csv_redshift(table,
                columns, csv_path, iam_role, region))
        else:
            if 's3' in csv_path:
                path = csv_path.split('/')[-1]
                self.s3.download_file(path)
                self.connection.execute(
                                            self.q.get_load_csv(
                                                table,
                                                columns,
                                                "/tmp/{}".format(path)
                                            )
                                        )
                os.remove("/tmp/{}".format(path))
            else:
                self.connection.execute(self.q.get_load_csv(table, columns, csv_path))

        self.mark_uploaded(filename, table)

    def safe_query(self, query):
        result = None
        trans = self.connection.begin()
        try:
            result = self.connection.execute(query)
            trans.commit()
        except Exception as e:
            trans.rollback()
            raise e
        return result

    def drop_tables(self):
        for query in self.q.get_drop_queries()._asdict().values():
            self.connection.execute(query)

    def close_connection(self):
        self.connection.close()

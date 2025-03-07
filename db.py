import logging
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Log level: INFO, DEBUG, ERROR, etc.
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler("database_module.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)

class DatabaseAwsModule:
    def __init__(self, db_url):
        """
        Initialize the database module.

        :param db_url: Database connection string.
        """
        try:
            self.engine = create_engine(db_url)
            self.metadata = MetaData()
            self.table_name = 'application_store_status'
            self.store_status_table = None
            self._reflect_table()
            logging.info("Database module initialized successfully.")
        except Exception as e:
            logging.critical(f"Failed to initialize the database module: {e}")

    def _reflect_table(self):
        """
        Reflect the existing table schema.
        """
        try:
            self.store_status_table = Table(self.table_name, self.metadata, autoload_with=self.engine)
            logging.info(f"Table '{self.table_name}' reflected successfully.")
            logging.debug(f"Available columns: {self.store_status_table.columns.keys()}")
        except Exception as e:
            logging.error(f"Error reflecting table '{self.table_name}': {e}")
            raise

    def insert_status(self, store_id, cam_no, status, script_name, company):
        """
        Insert or update the camera status in the application_store_status table.

        :param store_id: Store ID.
        :param cam_no: Camera number.
        :param status: Status (e.g., Running or Not Running).
        :param script_name: Name of the script being monitored.
        """
        now = datetime.utcnow()  # Use a datetime object, not a formatted string
        try:
            with self.engine.begin() as connection:  # Use `begin()` for auto-commit
                insert_query = self.store_status_table.insert().values(
                    store_id=store_id,
                    cam_no=cam_no,
                    status=status,
                    script_name=script_name,
                    created_at=now,
                    company=company
                )
                result = connection.execute(insert_query)
                logging.info(f"Insert successful for store_id={store_id}, cam_no={cam_no}. Rows affected: {result.rowcount}")
        except Exception as e:
            logging.error(f"Error inserting data for store_id={store_id}, cam_no={cam_no}: {e}")

#if __name__ == "__main__":
#    try:
#        db_module = DatabaseAwsModule('mysql+pymysql://admin:Saigroup987@internal-dev.cc6e5l3lii71.eu-west-2.rds.amazonaws.com/iceland_application')
#        db_module.insert_status(1, 12, "Not Running", "D:\\Sai_Group\\customer_aisle_interaction\\torch_env\\Scripts\\python main.py")
#    except Exception as e:
#        logging.critical(f"Critical error in the main program: {e}")
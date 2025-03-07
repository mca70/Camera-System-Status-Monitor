'''
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table

# Create the database engine
engine = create_engine("mysql+pymysql://userdb:Saigroup%40987@centraldb.mysql.database.azure.com/checkov1_iceland_db", echo=True)

# Reflect the existing table
metadata = MetaData()
records_table = Table("status", metadata, autoload_with=engine)

# Debugging: Print all columns in the table
print("Available columns:", records_table.columns.keys())

# Calculate the time range (last 15 minutes)
now = datetime.utcnow()
fifteen_minutes_ago = now - timedelta(minutes=30)

print(now, fifteen_minutes_ago)
# Query using SQLAlchemy Core
with engine.connect() as connection:
    query = records_table.select().where(
        records_table.c.updated_at.between(fifteen_minutes_ago, now) & (records_table.c.store_id==1) & (records_table.c.camera_no == 13)
    )
    result = connection.execute(query)

    # Fetch all matching records
    records = result.fetchall()

# Print the results
for record in records:
    print("---->", record)
    

'''
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table

class DatabaseModule:
    def __init__(self, db_url, table_name):
        """
        Initialize the database module.

        :param db_url: Database connection string.
        :param table_name: Name of the table to interact with.
        """
        self.engine = create_engine(db_url)#, echo=True)
        self.metadata = MetaData()
        self.table_name = table_name
        self.table = None
        self._reflect_table()

    def _reflect_table(self):
        """
        Reflect the existing table schema.
        """
        self.table = Table(self.table_name, self.metadata, autoload_with=self.engine)
        #print("Available columns:", self.table.columns.keys())

    def fetch_recent_records(self, store_id, camera_no, minutes=30):
        """
        Fetch records from the last `minutes` for the specified store_id and camera_no.

        :param store_id: Store ID to filter records.
        :param camera_no: Camera number to filter records.
        :param minutes: Number of minutes to look back for records.
        :return: List of matching records.
        """
        now = datetime.utcnow()
        time_threshold = now - timedelta(minutes=minutes)
        
        # Format datetime objects as strings
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        time_threshold = time_threshold.strftime('%Y-%m-%d %H:%M:%S')

        #print(f"Current Time: {now}, Time Threshold: {time_threshold}")

        with self.engine.connect() as connection:
            query = self.table.select().where(
                self.table.c.updated_at.between(time_threshold, now) &
                (self.table.c.store_id == store_id) &
                (self.table.c.camera_no == camera_no)
            )
            result = connection.execute(query)
            return result.fetchall()

'''
if __name__ == "__main__":
    # Read configuration
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    DB_URL = config.get("database", "db_url", raw=True)
    TABLE_NAME = config["database"]["table_name"]
    STORE_ID = int(config["query"]["store_id"])
    CAMERA_NOs = config["query"]["camera_no"].split(', ')
    TIME_RANGE_MINUTES = int(config["query"]["time_range_minutes"])

    # Create a DatabaseModule instance
    db_module = DatabaseModule(DB_URL, TABLE_NAME)
    
    cam_status_output = {}
    for CAMERA_NO in CAMERA_NOs:
        # Fetch recent records
        records = db_module.fetch_recent_records(STORE_ID, CAMERA_NO, TIME_RANGE_MINUTES)

        if len(records) > 4:
            cam_status_output[CAMERA_NO] = 'Not Running'
            #print(f"System Running for CAMERA_NO: {CAMERA_NO}")
            
    print(cam_status_output)
'''
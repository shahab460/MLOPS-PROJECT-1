import os
import pandas as pd
from google.cloud import storage
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml
import yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]
        
        # Initialize Google Cloud Storage client
        #self.client = storage.Client.from_service_account_json(
        #    self.config["credentials_path"],  # Add credentials path to config
        #    project=self.config["project_id"]  # Add project ID to config
        #)

        ## shah ##
        # Initialize Google Cloud Storage client using environment variable
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at {credentials_path}")
        logger.info(f"Loading credentials from: {credentials_path}")
        self.client = storage.Client.from_service_account_json(
            credentials_path,
            project=self.config["project_id"]
        )
        ## end shah ##

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data ingestion started with {self.bucket_name} and file is {self.file_name}")

    def download_csv_from_gcp(self):
        try:
            #client = storage.Client
            #bucket = client.bucket(self.bucket_name)
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(self.file_name)

            blob.download_to_filename(RAW_FILE_PATH)

            logger.info(f"CSV file successfully downloaded to {RAW_FILE_PATH}")

        except Exception as e:
            logger.error("Error while downloading csv file")
            raise CustomException("Failed to download csv file",e)
        
    def split_data(self):
        try:
            logger.info("Starting the split data process")
            data = pd.read_csv(RAW_FILE_PATH)

            train_data, test_data = train_test_split(data, test_size=1-self.train_test_ratio, random_state=42)

            train_data.to_csv(TRAIN_FILE_PATH)
            test_data.to_csv(TEST_FILE_PATH)

            logger.info(f"Train data saved to {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved to {TEST_FILE_PATH}")

        except Exception as e:
            logger.error("Error while splitting data")
            raise CustomException("Failed to split data",e)
            
    def run(self):
        try:
            logger.info("Starting the run method")

            self.download_csv_from_gcp()
            self.split_data()

            logger.info("Data ingestion completed successfully")

        except Exception as e:
            logger.error("Error during run")
            raise CustomException("Failed to run",e)
        finally:
            logger.info("Data ingestion completed")

if __name__ == "__main__":
    with open(CONFIG_PATH,'r') as file:
        config = yaml.safe_load(file)
    #data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion = DataIngestion(config)
    data_ingestion.run()
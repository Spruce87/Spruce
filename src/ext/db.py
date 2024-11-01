from pymongo import MongoClient
import os
from ext import Logger

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        """Initialize MongoDB connections and configuration data"""
        if hasattr(self, 'maindb'):  # Check if already loaded
            return
        try:
            # Primary MongoDB client and collections
            Logger.info("Database Connecting...")
            self.maindb = MongoClient(os.environ["mongo_url"])
            self.cfdbc = self.maindb["configdb"]["configdbc"]
            self.dbc = self.maindb["tourneydb"]["tourneydbc"]
            self.scrimdbc = self.maindb["tourneydb"]["scrimdbc"]
            self.paydbc = self.maindb["paymentdb"]["paymentdbc"]
            self.primedbc = self.maindb["primedb"]["primedbc"]
            self.guildbc = self.maindb["guildb"]["guildbc"]

            # Load configuration data from the main config collection
            self.cfdata = dict(self.cfdbc.find_one({"config_id": 87}))
            self.token = self.cfdata.get(os.environ["tkn"])
            self.GEMAPI = self.cfdata["gemapi"]
            self.spot_id = self.cfdata["spot_id"]
            self.spot_secret = self.cfdata["spot_secret"]
            self.bws = self.cfdata["bws"]
            self.m_host = self.cfdata["m_host"]
            self.m_host_psw = self.cfdata.get("m_host_psw")
            self.gh_api = self.cfdata.get("git_api")
            # Secondary MongoDB client based on a config value, if necessary
            self.spdb = MongoClient(self.cfdata.get("spdb"))
            Logger.info("Database Connected.")
   
        except Exception as e:
            Logger.warning(f"Error loading database or configuration data: {e}")



    



# # Usage
# db_instance = Database()  # The singleton instance
# print(db_instance.token)   # Access the configuration data

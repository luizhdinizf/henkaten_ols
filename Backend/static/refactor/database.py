from pymongo import MongoClient
client = MongoClient("mongodb://brmtz-dev-001:27017/")
database = client["henkaten_ols"]
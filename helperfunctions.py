from google.cloud import datastore 
import re
from app import *

REGION = "me-west1"
PROJECT = "commit-automation"
client = datastore.Client(project="commit-automation",database="customer-billing-accounts-ids")

def get_billingaccount_names():
    key = client.key('customer-billing-accounts-ids', 'Customer Name')
    names = list(client.get(key))
    return names
    
def get_billingaccount_id(name): 
    key = client.key('customer-billing-accounts-ids', 'Customer Name')
    ids = dict(client.get(key))
    return ids[name]
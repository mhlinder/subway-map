from pandas import read_csv
import pickle

stops = pickle.load(open('save/stops.p','rb'))
transfers = read_csv('indata/google_transit/transfers.txt')


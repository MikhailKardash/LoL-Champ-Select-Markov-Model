# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 17:17:35 2019

@author: Michael K
"""

import numpy as np
import pandas as pd
from data_functions import *
import time

start_time = time.time()

data = np.load('datamap_file.npy')

team_A_picks = [72];
team_B_picks = [34];


#team_A_picks = [21];
#team_B_picks = [92,51];

champ_info = pd.read_csv("champs.csv")
info = champ_info.values
champ_inds = info[:,1].astype("int64")


[champs,probs,games] = run_alg(team_A_picks,team_B_picks,data,champ_inds,60)
print(champs)
print(probs)
print(games)
print("--- %s seconds ---" % (time.time() - start_time))
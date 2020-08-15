# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 15:42:00 2019

@author: Michael K
"""

import numpy as np


def run_alg(team_A_list,team_B_list,data,champ_inds,topN):
    num = pick_num(team_A_list,team_B_list)
    flag = False
    if not isAPicking(num,flag):
        data = flipinds(data)
        flag = True
        print("Flipping data for B side")
        temp = team_A_list.copy()
        team_A_list = team_B_list.copy()
        team_B_list = temp.copy()
    winspace = create_constrained_space(data.copy(),team_A_list,team_B_list)
    losspace = create_constrained_space(flipinds(data),team_A_list,team_B_list)
    print(len(winspace))
    print(len(losspace))
    champs = generate_champ_list(team_A_list,team_B_list,champ_inds)
    prob = create_champ_probability(winspace,losspace,num,champs,team_A_list,team_B_list,champ_inds,flag)
    prob_F = create_final_prob(prob)
    #return get_amax(prob_F,topN)
    return alternate_amax(prob_F,topN)

def flipinds(space):
    temp = np.asarray(space)
    return np.stack([temp[:,1,:],temp[:,0,:]],1)

def pick_num(team_A_list,team_B_list):
    num_picks = len(team_A_list) + len(team_B_list)
    selNo= num_picks + 1
    return selNo

def create_constrained_space(space,team_A_list,team_B_list):
    out = space
    if len(team_A_list) > 0:
        for A in team_A_list:
            out = [el for el in out if A in el[0]]
    if len(team_B_list) > 0:
        for B in team_B_list:
            out = [el for el in out if B in el[1]]
    return out

def generate_champ_list(team_A_list,team_B_list,champ_inds):
    A = champ_inds.copy()
    A = [el for el in A if el not in team_A_list]
    return [el for el in A if el not in team_B_list]

def get_amax(probs,topN):
    temp = np.asarray(probs)
    inds = np.argsort(temp[:,1]).tolist()
    champs = temp[inds[-topN:],0]
    probs = temp[inds[-topN:],1]
    return [np.flip(champs), np.flip(probs)]

def alternate_amax(probs,topN):
    temp = np.asarray(probs)
    p_vec = np.unique(temp[:,1])
    p_vec = np.flip(np.sort(p_vec))
    inds_final = [];
    for el in p_vec:
        inds = np.argwhere(temp[:,1] == el) #find inds of probs.
        inds = np.squeeze(inds)
        inds = inds.tolist()
        temp2 = temp[inds,:] #isolate probs we're interested in
        if isinstance(inds,int):
            inds_final = [*inds_final, inds]
        else:
            temp2 = np.reshape(temp2,[len(inds),temp2.shape[-1]])
            inds_F = np.argsort(temp2[:,2]) #sort new data by win number
            inds_F = np.flip(inds_F).tolist() #get in decreasing order
            inds = np.asarray(inds)
            inds_final = [*inds_final, *inds[inds_F]]
    out = temp[inds_final]
    return [out[:,0],out[:,1],out[:,2]]
        
        

def get_winloss(winspace,lossspace,champ_list,flag):
    out = [];
    for num in champ_list:
        #last pick is always team B.
        if not flag:
            win_games = [el for el in winspace if num in el[1]]
            loss_games = [el for el in lossspace if num in el[1]]
        else:
            win_games = [el for el in winspace if num in el[0]]
            loss_games = [el for el in lossspace if num in el[0]]
        out.append([num,len(win_games),len(loss_games)])
    return np.asarray(out)
    
def marginalize(probs):
    temp = np.asarray(probs)
    wins = np.sum(temp[:,1])
    losses = np.sum(temp[:,2])
    #normalization = wins + losses
    #if normalization == 0:
    #    return [0,0]
    #else:
    #    return [wins/normalization, losses/normalization]
    return [wins,losses]

def isAPicking(numb,flag):
    if (numb is 1) or (numb is 4) or (numb is 5) or (numb is 8) or (numb is 9):
        return not flag
    else:
        return flag
    
def create_final_prob(inmat):
    out = [];
    for el in inmat:
        if (el[1] + el[2]) > 0:
            numgames = el[1] + el[2]
            winrate = el[1]/(numgames);
        else:
            numgames = 0;
            winrate = 0;
        out.append([el[0],winrate,numgames])
    return out
    
def create_champ_probability(winspace,lossspace,num,champ_list,team_A_list,team_B_list,champ_inds,flag):
    if num is 10:
        return get_winloss(winspace,lossspace,champ_list,flag)
    elif num is 11:
        return 0
    else:
        out = [];
        for champ in champ_list:
            if isAPicking(num,flag):
                newA = [champ]
                newwin = create_constrained_space(winspace,newA,[])
                newloss = create_constrained_space(lossspace,newA,[])
                if len(newwin) is 0 and len(newloss) is 0:
                    out.append([champ,0,0])
                else:
                    newchamps = generate_champ_list(newA,[],champ_list)
                    temp = create_champ_probability(newwin,newloss,num+1,newchamps,newA,[],champ_inds,flag)
                    marg = marginalize(temp)
                    out.append([champ,marg[0],marg[1]])   
            else:
                newB = [champ]
                newwin = create_constrained_space(winspace,[],newB)
                newloss = create_constrained_space(lossspace,[],newB)
                if len(newwin) is 0 and len(newloss) is 0:
                    out.append([champ,0,0])
                else:    
                    newchamps = generate_champ_list([],newB,champ_list)
                    temp = create_champ_probability(newwin,newloss,num+1,newchamps,[],newB,champ_inds,flag)
                    marg = marginalize(temp)
                    out.append([champ,marg[0],marg[1]])      
        return np.asarray(out)
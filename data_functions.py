# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 15:42:00 2019

@author: Michael K
"""

import numpy as np


def run_alg(team_a_list, team_b_list, data, champ_inds):
    num = pick_num(team_a_list, team_b_list)
    flag = False
    if not is_a_picking(num, flag):
        data = flipinds(data)
        flag = True
        print("Flipping data for B side")
        temp = team_a_list.copy()
        team_a_list = team_b_list.copy()
        team_b_list = temp.copy()
    winspace = create_constrained_space(data.copy(),
                                        team_a_list,
                                        team_b_list)
    losspace = create_constrained_space(flipinds(data),
                                        team_a_list,
                                        team_b_list)
    #  print(len(winspace))
    #  print(len(losspace))
    champs = generate_champ_list(team_a_list, team_b_list,
                                 champ_inds)
    prob = create_champ_probability(winspace, losspace,
                                    num, champs,  champ_inds, flag)
    final_prob = create_final_prob(prob)
    return alternate_amax(np.asarray(final_prob))


def flipinds(space):
    temp = np.asarray(space)
    return np.stack([temp[:, 1, :], temp[:, 0, :]], 1)


def pick_num(team_a_list, team_b_list):
    num_picks = len(team_a_list) + len(team_b_list)
    selection_num = num_picks + 1
    return selection_num


def create_constrained_space(space, team_a_list, team_b_list):
    out = space
    if len(team_a_list) > 0:
        for A in team_a_list:
            out = [el for el in out if A in el[0]]
    if len(team_b_list) > 0:
        for B in team_b_list:
            out = [el for el in out if B in el[1]]
    return out


def generate_champ_list(team_a_list, team_b_list, champ_inds):
    valid = champ_inds.copy()
    valid = [el for el in valid if el not in team_a_list]
    return [el for el in valid if el not in team_b_list]


def get_amax(probs, top_n):
    temp = np.asarray(probs)
    inds = np.argsort(temp[:, 1]).tolist()
    champs = temp[inds[-top_n:], 0]
    probs = temp[inds[-top_n:], 1]
    return [np.flip(champs), np.flip(probs)]


def alternate_amax(probs):
    inds = np.lexsort((probs[:, 2], probs[:, 1]))
    return probs[inds,:]
        

def get_winloss(winspace, lossspace, champ_list, flag):
    out = []
    for num in champ_list:
        # last pick is always team B.
        if not flag:
            win_games = [el for el in winspace if num in el[1]]
            loss_games = [el for el in lossspace if num in el[1]]
        else:
            win_games = [el for el in winspace if num in el[0]]
            loss_games = [el for el in lossspace if num in el[0]]
        out.append([num, len(win_games), len(loss_games)])
    return np.asarray(out)


def marginalize(probs):
    temp = np.asarray(probs)
    wins = np.sum(temp[:, 1])
    losses = np.sum(temp[:, 2])
    # normalization code left if necessary.
    '''
    normalization = wins + losses
    if normalization == 0:
        return [0,0]
    else:
        return [wins/normalization, losses/normalization]
    '''
    return [wins, losses]


def is_a_picking(numb, flag):
    if (numb == 1) or (numb == 4) or (numb == 5) or (numb == 8) or (numb == 9):
        return not flag
    else:
        return flag


def create_final_prob(inmat):
    out = []
    for el in inmat:
        if (el[1] + el[2]) > 0:
            numgames = el[1] + el[2]
            winrate = el[1]/numgames
        else:
            numgames = 0
            winrate = 0
        out.append([el[0], winrate, numgames])
    return out


def create_champ_probability(winspace, lossspace,
                             num, champ_list,
                             champ_inds, flag):
    if num == 10:
        return get_winloss(winspace, lossspace,
                           champ_list, flag)
    elif num == 11:
        return 0
    else:
        out = []
        for champ in champ_list:
            if is_a_picking(num, flag):
                new_a = [champ]
                newwin = create_constrained_space(winspace, new_a, [])
                newloss = create_constrained_space(lossspace, new_a, [])
                if len(newwin) == 0 and len(newloss) == 0:
                    out.append([champ, 0, 0])
                else:
                    newchamps = generate_champ_list(new_a, [], champ_list)
                    temp = create_champ_probability(newwin, newloss,
                                                    num+1, newchamps,
                                                    champ_inds, flag)
                    marg = marginalize(temp)
                    out.append([champ, marg[0], marg[1]])
            else:
                new_b = [champ]
                newwin = create_constrained_space(winspace, [], new_b)
                newloss = create_constrained_space(lossspace, [], new_b)
                if len(newwin) == 0 and len(newloss) == 0:
                    out.append([champ, 0, 0])
                else:    
                    newchamps = generate_champ_list([], new_b, champ_list)
                    temp = create_champ_probability(newwin, newloss,
                                                    num+1, newchamps,
                                                    champ_inds, flag)
                    marg = marginalize(temp)
                    out.append([champ, marg[0], marg[1]])
        return np.asarray(out)

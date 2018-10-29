# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 22:39:00 2018

@author: user
"""

import random

class Dude:
    def __init__(self, id):
        self.awesomeness = random.normalvariate(100, 20)
        self.num_matches = 0
        
    def reported_awesomeness(self):
        self.num_matches += 1
        return random.normalvariate(self.awesomeness, 10)
    
    def __lt__(self, other):
        return self.reported_awesomeness() < other.reported_awesomeness()
    
    def __repr__(self):
        return "Dude ({} / {})".format(self.awesomeness, self.num_matches)


def standard_sort(xs):
    return sorted(xs, reverse=True)

def bubble_sort(xs):
    ys = xs.copy()
    n = len(ys)
    is_swapped = True
    count = 0
    while is_swapped:
        count += 1
        if count >= n:
            break
        is_swapped = False
        for i in range(1, n):
            if ys[i - 1] < ys[i]:
                ys[i-1], ys[i] = ys[i], ys[i-1]
                is_swapped = True
    return ys   

def knockout_round(xs):
    ys = xs.copy()
    n = len(ys)
    assert (n % 2) == 0
    
    best = []
    worst = []
    
    while len(ys) > 0:
        p1 = ys.pop(0)
        p2 = ys.pop(0)
        if p1 > p2:
            best.append(p1)
            worst.append(p2)
        else:
            best.append(p2)
            worst.append(p1)
    return best, worst

def knockout(xs):
    best = xs
    bests = [] 
    worsts = []
    while len(best) > 8:
        best, worst = knockout_round(best)
        bests.append(best)
        worsts.append(worst)
        
    ys = []
    for w in worsts:
        ys += w
    ys += bests[-1]
    ys.reverse()
    return ys    

def elo(xs):
    ys = xs.copy()
    n = len(ys)
    num_games = 2000
    for y in ys:
        y.elo = 1500
        
    for i in range(num_games):
        competitor_indexes = random.sample(range(n), 2)
        i1 = competitor_indexes[0]
        i2 = competitor_indexes[1]
        rating1 = ys[i1].elo
        rating2 = ys[i2].elo
        expected_score1 = 1.0 / (1 + 10**((rating2 - rating1)/400))
        expected_score2 = 1.0 - expected_score1
        if ys[i1] > ys[i2]:
            actual_score1 = 1.0
            actual_score2 = 0.0
        else:
            actual_score1 = 0.0
            actual_score2 = 1.0
        # new ratings
        ys[i1].elo = rating1 + 32.0 * (actual_score1 - expected_score1)
        ys[i2].elo = rating1 + 32.0 * (actual_score2 - expected_score2)
    
    ys.sort(key=lambda y: y.elo, reverse=True)
    return ys    
        

def evaluate(fcn):
    individuals = [Dude(i) for i in range(n_pop)]
    true_sorted_dudes = sorted(individuals, key=lambda d: d.awesomeness, reverse=True)
    #true_best = true_sorted_dudes[:n_sel]
    true_worst = true_sorted_dudes[n_sel:]
    
    sorted_individuals = fcn(individuals)
    
    best = sorted_individuals[:n_sel]
    #worst = sorted_individuals[n_sel:]
    
    num_wrong = len([x for x in best if x in true_worst])
    
    
    total_matches = sum([d.num_matches for d in sorted_individuals]) / 2
    
    print("Evaluating {}".format(fcn.__name__))
    print("Total matches = {}".format(total_matches))
    print("{}/{} wrongly classified as best".format(num_wrong, n_sel))
    print("")
    for d in sorted_individuals:
        #print(d)
        pass
        


if __name__ == "__main__":
    n_pop = 64
    n_sel = 8
    evaluate(standard_sort)
    evaluate(bubble_sort)
    evaluate(knockout)
    evaluate(elo)

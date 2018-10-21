import random
import gamelib

class RandomStrategyData:
    def __init__(self, my_side, friendly_edge_locations, config):
        self.friendly_edge_locations = friendly_edge_locations
        self.my_side = my_side
        self.init_config(config)
        
    def init_config(self, config):
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        
        
    def randomise(self):
        self.filter_likelihoods = {}
        self.destructor_likelihoods = {}
        self.encryptor_likelihoods = {}
        for loc in self.my_side:
            x = loc[0]
            y = loc[1]
            self.filter_likelihoods[x, y] = random.random()
            self.destructor_likelihoods[x, y] = random.random()
            self.encryptor_likelihoods[x, y] = random.random()
        
        self.ping_likelihoods = {}
        self.emp_likelihoods = {}
        self.scrambler_likelihoods = {}
        for loc in self.friendly_edge_locations:
            x = loc[0]
            y = loc[1]
            self.ping_likelihoods[x, y] = random.random()
            self.emp_likelihoods[x, y] = random.random()
            self.scrambler_likelihoods[x, y] = random.random()
            
        self.likelihoods = {}
        self.likelihoods[PING] = self.ping_likelihoods
        self.likelihoods[EMP] = self.emp_likelihoods
        self.likelihoods[SCRAMBLER] = self.scrambler_likelihoods
        self.likelihoods[FILTER] = self.filter_likelihoods
        self.likelihoods[DESTRUCTOR] = self.destructor_likelihoods
        self.likelihoods[ENCRYPTOR] = self.encryptor_likelihoods
        
        self.update_precalc()
    
    def mutate(self):
        # vary each number using a normal distribution
        std_dev = 0.02
        maximum = 1.0
        minimum = 0.0
        for unit_type, likelihood_dict in self.likelihoods.items():
            for loc, value in likelihood_dict.items():
                likelihood_dict[loc] += random.normalvariate(0.0, std_dev)
                if likelihood_dict[loc] > maximum:
                    likelihood_dict[loc] = maximum
                elif likelihood_dict[loc] < minimum:
                    likelihood_dict[loc] = minimum
    
    def update_precalc(self):
        self.sums = {}
        for unit_type in self.likelihoods:
            self.sums[unit_type] = sum([self.likelihoods[unit_type][loc] for loc in self.likelihoods[unit_type]])
            
        self.ordered_lists = {}
        for unit_type in self.likelihoods:
            self.ordered_lists[unit_type] = [x for x in self.likelihoods[unit_type].items()] # [((x,y), k)]
        
        self.defence_sum = self.sums[FILTER] + self.sums[ENCRYPTOR] + self.sums[DESTRUCTOR]
        self.attack_sum = self.sums[PING] + self.sums[EMP] + self.sums[SCRAMBLER]
       
    def choose_defence_move(self):
        x = random.random() * self.defence_sum
        if x < self.sums[FILTER]:
            # choose a filter location
            return self.choose_cumulative_item(FILTER, x)
        elif x < (self.sums[FILTER] + self.sums[ENCRYPTOR]):
            # choose an encryptor location
            return self.choose_cumulative_item(ENCRYPTOR, x - self.sums[FILTER])
        else:
            # choose a destructor location
            return self.choose_cumulative_item(DESTRUCTOR, x - self.sums[FILTER] - self.sums[ENCRYPTOR])
        
    def choose_attack_move(self):
        x = random.random() * self.attack_sum
        if x < self.sums[PING]:
            # choose a ping location
            return self.choose_cumulative_item(PING, x)
        elif x < (self.sums[PING] + self.sums[EMP]):
            # choose an emp location
            return self.choose_cumulative_item(EMP, x - self.sums[PING])
        else:
            # choose a Scrambler location
            return self.choose_cumulative_item(SCRAMBLER, x - self.sums[PING] - self.sums[EMP])
    
    def choose_cumulative_item(self, unit_type, random_var):
        cumulative_sum = 0.0
        for ((x, y), k) in self.ordered_lists[unit_type]:
            cumulative_sum += k
            if cumulative_sum > random_var:
                return ([x, y], unit_type)
    
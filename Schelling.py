from numpy import random, mean

"""
Homework 3: Modify the Agent Based Model from class.
1. Add the following things to the params dict, and make the program use those
   settings:
   A boolean for whether or not to print results to the screen,
   a boolean for whether or not to save results to file, and
   a setting for the location to write the output to on your computer.
2. The current move method lets agents look through all vacant patches, and then
   picks the first one that makes them happy.
   Write a new move method, or modify the existing one, so that you have
   the option of simply moving the agent to a random free location without
   first checking happiness.
   Add a parameter that switches between these two move processes.
3. It is currently hard-coded that there are two types of agents, each of whom
   make up half of the population and have the same preference for similar
   neighbors.
   Change it so that the proportion of reds and blues is adjustable,
   and each one should be able to have a different same_pref.
   Change the report method to show results split by color.
"""


#note: update out_path to point to somewhere on your computer
params = {'world_size':(20,20),
          'num_agents':380,
          'same_pref_r' :0.4,
          'same_pref_b':0.7, #3 here, need to make variable? so one for r one for b?
          'max_iter'  :100,
          'proportion_r': 0.3 #,#3? still need to add same_pref adjustability
          #'out_path': (r'my path')} #1? plus some boulians?
          }

class Agent():
    def __init__(self, world, kind, same_pref_r, same_pref_b):
        self.world = world
        self.kind = kind
        self.same_pref_r = same_pref_r #3 here! do something here?
        self.same_pref_b = same_pref_b
        self.location = None

    def move(self):
        #handle each agent's turn in the model iteration
        #returns 0 for happy, 1 for unhappy but moved, and 2 for unhappy and couldn't move

#2 here! something here to add randomization of enter loop or move randomly w/o checking
#vacancies = self.world.find_vacant(return_all=True)
#move
#do_i_like_it = self.am_i_happy()
#    if do_i_like_it is True:
#        return 1
#    if do_i_like_it is False:
#        return 2

#from later in the code:
       #finds all empty patches on the grid and returns a random one, unless kwarg return_all==True,
        #then it returns a list of all empty patches

#        empties = [loc for loc, occupant in self.grid.items() if occupant is None]
#        if return_all:
#            return empties
#        else:
#            choice_index = random.choice(range(len(empties)))
#            return empties[choice_index]

        happy = self.am_i_happy()

        if not happy:
            vacancies = self.world.find_vacant(return_all=True)
            for patch in vacancies:
                i_moved = False
                will_i_like_it = self.am_i_happy(loc=patch)
                if will_i_like_it is True:
                    self.world.grid[self.location] = None #move out of current patch
                    self.location = patch                 #assign new patch to myself
                    self.world.grid[patch] = self         #update the grid
                    i_moved = True
                    # break
                    return 1
#             if not i_moved:
            if i_moved is False:
                return 2
        else:
            return 0

    def am_i_happy(self, loc=False, neighbor_check=False):
        #this should return a boolean for whether or not an agent is happy at a location
        #if loc is False, use current location, else use specified location

        if not loc:
            starting_loc = self.location
        else:
            starting_loc = loc

        neighbor_patches = self.world.locate_neighbors(starting_loc)
        neighbor_agents  = [self.world.grid[patch] for patch in neighbor_patches]
        neighbor_kinds   = [agent.kind for agent in neighbor_agents if agent is not None]
        num_like_me      = sum([kind == self.kind for kind in neighbor_kinds])

        #for reporting purposes, allow checking of the current number of similar neighbors
        if neighbor_check:
            return [kind == self.kind for kind in neighbor_kinds]

        #if an agent is in a patch with no neighbors at all, treat it as unhappy
        if len(neighbor_kinds) == 0:
            return False

        perc_like_me = num_like_me / len(neighbor_kinds)
#3 hard coded same_pref
#now need to know agent's kind then can do the if statement:
#this one is for red
        if perc_like_me < self.same_pref_r:
            return False
        else:
            return True

'''
added debug statements back in from class


        #intermediat output to check on stuff:
        if perc_like_me < self.same_pref:
            if not loc: #debug
                print('Me:',self.kind) #debug
                print('My neighbors:', neighbor_kinds) #debug
                print('{} < {}'.format(perc_like_me, self.same_pref)) #debug
                print('Not happy.') #debug
            return False
        else:
            if not loc: #debug
                print('Me:',self.kind) #debug
                print('My neighbors:', neighbor_kinds) #debug
                print('{} >= {}'.format(perc_like_me, self.same_pref)) #debug
                print('Happy!') #debug
            return True

end added debug statements
'''


class World():
    def __init__(self, params):
        assert(params['world_size'][0] * params['world_size'][1] > params['num_agents']), 'Grid too small for number of agents.'
        self.params = params
        self.reports = {}

        self.grid     = self.build_grid(  params['world_size'])
        self.agents   = self.build_agents(params['num_agents'], params['same_pref_r'],
                                          params['same_pref_b'], params['proportion_r'])

        self.init_world()

    def build_grid(self, world_size):
        #create the world that the agents can move around on
        locations = [(i,j) for i in range(world_size[0]) for j in range(world_size[1])]
        return {l:None for l in locations}

    def build_agents(self, num_agents, same_pref_r, same_pref_b, proportion_r):
        #generate a list of Agents that can be iterated over

#3, hard code for 1/2 need to change the 2 to ref a parameter
#'proportion_r_b': (0.5,0.5)
        def _kind_picker(i):
            if i < round(num_agents * proportion_r):
                return 'red'
            else:
                return 'blue'

'''
check

num_agents = 10
proportion_r = 0.9
my_test_agents = [_kind_picker(i) for i in range(num_agents)]
my_test_agents

check
'''
        def _pref_picker(i): #added a function so that agents can have diff prefs
            if i < round(num_agents * proportion_r):
                return same_pref_r
            else:
                return same_pref_b

'''
check

same_pref_r = 0.3
same_pref_b = 0.7
my_test_pref = [_pref_picker(i) for i in range(num_agents)]
my_test_pref
'''

'''
Help, what does Agent mean in this context?
'''
                                                #changed so that calls my helper fn
        agents = [Agent(self, _kind_picker(i), _pref_picker(i)) for i in range(num_agents)]
        random.shuffle(agents)
        return agents

'''check:fail
agents = [Agent(_kind_picker(i), _pref_picker(i)) for i in range(num_agents)]
agents
build_agents()
'''



    def init_world(self):
        #a method for all the steps necessary to create the starting point of the model

        for agent in self.agents:
            loc = self.find_vacant()
            self.grid[loc] = agent
            agent.location = loc

        assert(all([agent.location is not None for agent in self.agents])), "Some agents don't have homes!"
        assert(sum([occupant is not None for occupant in self.grid.values()]) == self.params['num_agents']), 'Mismatch between number of agents and number of locations with agents.'

        #set up some reporting dictionaries
        self.reports['integration'] = []

    def find_vacant(self, return_all=False):
        #finds all empty patches on the grid and returns a random one, unless kwarg return_all==True,
        #then it returns a list of all empty patches

        empties = [loc for loc, occupant in self.grid.items() if occupant is None]
        if return_all:
            return empties
        else:
            choice_index = random.choice(range(len(empties)))
            return empties[choice_index]

    def locate_neighbors(self, loc):
        #given a location, return a list of all the patches that count as neighbors
        include_corners = True

        x, y = loc
        cardinal_four = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        if include_corners:
            corner_four = [(x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)]
            neighbors = cardinal_four + corner_four
        else:
            neighbors = cardinal_four

        #handle patches that are at the edges, assuming a "torus" shape
        x_max = self.params['world_size'][0] - 1
        y_max = self.params['world_size'][1] - 1

        def _edge_fixer(loc):
            x, y = loc
            if x < 0:
                x = x_max
            elif x > x_max:
                x = 0

            if y < 0:
                y = y_max
            elif y > y_max:
                y = 0

            return (x, y)

        neighbors = [_edge_fixer(loc) for loc in neighbors]
        return neighbors

    def report_integration(self):
        diff_neighbors = []
        for agent in self.agents:
            diff_neighbors.append(sum(
                    [not a for a in agent.am_i_happy(neighbor_check=True)]
                                ))
        self.reports['integration'].append(round(mean(diff_neighbors), 2))
#1???
    def run(self):
        #handle the iterations of the model
        log_of_happy = []
        log_of_moved = []
        log_of_stay  = []
#this part is messed up by 2?
        self.report_integration()
        log_of_happy.append(sum([a.am_i_happy() for a in self.agents])) #starting happiness
        log_of_moved.append(0) #no one moved at startup
        log_of_stay.append(0) #no one stayed at startup

        for iteration in range(self.params['max_iter']):

            random.shuffle(self.agents) #randomize agents before every iteration
            move_results = [agent.move() for agent in self.agents]
            self.report_integration()

            num_happy_at_start = sum([r==0 for r in move_results])
            num_moved          = sum([r==1 for r in move_results])
            num_stayed_unhappy = sum([r==2 for r in move_results])

            log_of_happy.append(num_happy_at_start)
            log_of_moved.append(num_moved)
            log_of_stay .append(num_stayed_unhappy)

            if log_of_moved[-1] == log_of_stay[-1] == 0:
                print('Everyone is happy!  Stopping after iteration {}.'.format(iteration))
                break
            elif log_of_moved[-1] == 0 and log_of_stay[-1] > 0:
                print('Some agents are unhappy, but they cannot find anywhere to move to.  Stopping after iteration {}.'.format(iteration))
                break

        self.reports['log_of_happy'] = log_of_happy
        self.reports['log_of_moved'] = log_of_moved
        self.reports['log_of_stay']  = log_of_stay

        self.report()
#1
    def report(self, to_file=True):
        #report final results after run ends
        reports = self.reports
#update bc 2?
        print('\nAll results begin at time=0 and go in order to the end.\n')
        print('The average number of neighbors an agent has not like them:', reports['integration'])
        print('The number of happy agents:', reports['log_of_happy'])
        print('The number of moves per turn:', reports['log_of_moved'])
        print('The number of agents who failed to find a new home:', reports['log_of_stay'])

        if to_file:
            out_path = self.params['out_path']
            with open(out_path, 'w') as f:
                headers = 'turn,integration,num_happy,num_moved,num_stayed\n'
                f.write(headers)
                for i in range(len(reports['log_of_happy'])):
                    line = ','.join([str(i),
                                     str(reports['integration'][i]),
                                     str(reports['log_of_happy'][i]),
                                     str(reports['log_of_moved'][i]),
                                     str(reports['log_of_stay'][i]),
                                     '\n'
                                     ])
                    f.write(line)
            print('\nResults written to:', out_path)

world = World(params)
world.run()

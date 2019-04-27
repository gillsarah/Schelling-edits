from numpy import random, mean

#note: update out_path to point to somewhere on your computer

#well I broke it and I don't know how! It thinks they're happy, but I didn't
#touch am_i_happy or build_agents
#fixed it! Yay!

params = {'world_size':(20,20),
          'num_agents':380,
          #'same_pref' :0.4,
          'same_pref_r': 0.5,
          'same_pref_b': 0.3,
          'proportion_r': 0.6,
          'max_iter'  :20, #100
          'look_before_move': True, #toggle this T/F for Question 2
          'out_path':r'~\Desktop\Programing\HW_3\output.csv'} #not sure where it's going, but not there!

class Agent():
    def __init__(self, world, kind, same_pref):
        self.world = world
        self.kind = kind
        self.same_pref = same_pref
        #self.look_before_move = look_before_move
        self.location = None

    def move(self, params): #I added params
        #handle each agent's turn in the model iteration
        #returns 0 for happy, 1 for unhappy but moved, and 2 for unhappy and couldn't move

        happy = self.am_i_happy()

        if not happy and not params['look_before_move']:
        #enter this loop if the look_before_move parameter is set to False
        #handles moves for not happy but without checking if will be happy
        #at the new location
            #print("I'm in!") #debug
            vacancies1 = self.world.find_vacant(return_all=True)
            for patch in vacancies1:
                self.world.grid[self.location] = None #move out of current patch
                self.location = patch                 #assign new patch to myself
                self.world.grid[patch] = self         #update the grid
                return 3

        elif not happy and params['look_before_move']:
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
        elif happy: #needed to dubug! previously just else:
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

        if perc_like_me < self.same_pref:
            return False
        else:
            return True

class World():
    def __init__(self, params):
        assert(params['world_size'][0] * params['world_size'][1] > params['num_agents']), 'Grid too small for number of agents.'
        self.params = params
        self.reports = {}

        self.grid     = self.build_grid(params['world_size'])
        #self.agents   = self.agent_assign_helper(params['num_agents'])
        self.agents   = self.build_agents(params['num_agents'], params['same_pref_r'], params['same_pref_b'])
        
        self.init_world()

    
    #for i in range(params['num_agents']) : #works when num_agents <= 20 but out of range when > 380
    #    if world.agents[i].kind == 'red':
     #       their_pref = params['same_pref_r']
     #   else:
      #      their_pref = params['same_pref_b']
     

    #def agent_assign_helper(self, num_agents):
        #reduces the option of two preference parameters into one imput

        #length_to_itterate_over = params['num_agents'] #380
        #list_to_itterate_over = list(range(length_to_itterate_over)) #a list [0-279]
    #    for i in range(num_agents) : #works when num_agents <= 20 but out of range when > 380
    #        if world.agents[i].kind == 'red':
    #            same_pref = self.build_agents(params['num_agents'], params['same_pref_r'])
     #       else:
      #          my_agent = self.build_agents(params['num_agents'], params['same_pref_b'])
     #   return my_agent


    def build_grid(self, world_size):
        #create the world that the agents can move around on
        locations = [(i,j) for i in range(world_size[0]) for j in range(world_size[1])]
        return {l:None for l in locations}

    def build_agents(self, num_agents, same_pref_r, same_pref_b):
        #generate a list of Agents that can be iterated over

        def _kind_picker(i):
            if i < round(num_agents * params['proportion_r']):
                return 'red'
            else:
                return 'blue'

        def _pref_picker(i):
            if i < round(num_agents * params['proportion_r']):
                return params['same_pref_r']
            else:
                return params['same_pref_b']
        
        agents = [Agent(self, _kind_picker(i), _pref_picker(i)) for i in range(num_agents)]
        random.shuffle(agents)
        return agents
        #print('I built an agent') #why won't this work? Error: "unrechable code"
    

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

    def run(self): #altered this!!!!!!!!!!!!!
        #handle the iterations of the model
        log_of_happy = []
        log_of_moved = []
        log_of_stay  = []
        log_of_rand  = []

        self.report_integration()
        log_of_happy.append(sum([a.am_i_happy() for a in self.agents])) #starting happiness
        log_of_moved.append(0) #no one moved at startup
        log_of_stay.append(0) #no one stayed at startup

        for iteration in range(self.params['max_iter']):

            random.shuffle(self.agents) #randomize agents before every iteration
            move_results = [agent.move(params) for agent in self.agents]
            self.report_integration()

            num_happy_at_start = sum([r==0 for r in move_results])
            num_moved          = sum([r==1 for r in move_results])
            num_stayed_unhappy = sum([r==2 for r in move_results])
            num_moved_random   = sum([r==3 for r in move_results]) #addes this!!!!!!!!!!

            log_of_happy.append(num_happy_at_start)
            log_of_moved.append(num_moved)
            log_of_stay .append(num_stayed_unhappy)
            #log_of_moved.append(num_moved_random) #this way does not work, appends a 0 when shouldn't
            log_of_rand.append(num_moved_random) #debug

            #if not params[look_before_move]:
            #    print("we all just move, that's what we do")
            #else:
            #if log_of_moved[-1] == log_of_stay[-1] == 0:
            if log_of_happy[-1] == params['num_agents']:
                print('Everyone is happy!  Stopping after iteration {}.'.format(iteration))
                break
            elif log_of_moved[-1] == 0 and log_of_stay[-1] > 0:
                print('Some agents are unhappy, but they cannot find anywhere to move to.  Stopping after iteration {}.'.format(iteration))
                break

        self.reports['log_of_happy'] = log_of_happy
        self.reports['log_of_moved'] = log_of_moved
        self.reports['log_of_stay']  = log_of_stay
        self.reports['log_of_rand']  = log_of_rand

        self.report()

    def report(self, to_file=True):
        #report final results after run ends
        reports = self.reports

        print('\nAll results begin at time=0 and go in order to the end.\n')
        print('The average number of neighbors an agent has not like them:', reports['integration'])
        print('The number of happy agents:', reports['log_of_happy'])
        print('The number of moves per turn who checked if they would be happy:', reports['log_of_moved'])
        print('The number of moves per turn who did not check if they would be happy:', reports['log_of_rand'])
        print('The number of agents who failed to find a new home:', reports['log_of_stay'])
        print('check:',reports['log_of_rand']) #debug

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
a = 0 #debug
print(world.agents[a].kind) #debug
print(world.agents[a].same_pref) #debug

#tests at num_agents=20:
#for i in range(20):
#   print(world.agents[i].kind)
#check success: proportion is working

#for i in range(20):
#   print(world.agents[i].same_pref) 
#check success: pref is working


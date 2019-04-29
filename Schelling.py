from numpy import random, mean


#note: Project completed with the use of lecture notes, notes from TA discussion section, 
#and work on past assignements

#note: The provided code shows +2 results over number of itterations shown, 
# and if I run world.run() without running the rest of the code the output in incorrect.
#these errors are maintained 
#---no those make sense! 

#well I broke it and I don't know how! It thinks they're happy, but I didn't
#touch am_i_happy or build_agents
#fixed it! Yay!

#he wants integratoin too! what?

#out path not working correctly 

params = {'world_size':(20,20),
          'num_agents':380,
          'same_pref_r': 0.5,
          'same_pref_b': 0.3,
          'proportion_r': 0.6,
          'max_iter'  :100,
          'look_before_move': True, #toggle this T/F for Question 2
          'print_to_screen': True,  #toggle this T/F for Question 1
          'to_file': False,          #toggle this T/F for Question 1
          'out_path':r'c:\\users\\sarah\\desktop\\output.csv'} 

class Agent():
    def __init__(self, world, kind, same_pref):
        self.world = world
        self.kind = kind
        self.same_pref = same_pref
        self.location = None

    def move(self, params): #I added params
        #handle each agent's turn in the model iteration
        #returns 0 and 6 for happy
        #when look_before_move is True, agents check if they will be happy in a new location before moving
        #returns 1 and 7 for unhappy but moved, and 2 and 8 for unhappy and couldn't move
        #when look_before_move is False, unhappy agents do not check before moving
        #returns 4 and 5 for unhappy but moved, all agents who are unhappy move

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
                if self.kind == 'red':
                    return 4 #red moved
                else:
                    return 5 #blue moved

        elif not happy and params['look_before_move']:
        #enter this loop if the look_before_move parameter is set to True
        #handles moves for not happy, checking if will be happy at the new location
            vacancies = self.world.find_vacant(return_all=True)
            for patch in vacancies:
                i_moved = False
                will_i_like_it = self.am_i_happy(loc=patch)
                if will_i_like_it is True:
                    self.world.grid[self.location] = None #move out of current patch
                    self.location = patch                 #assign new patch to myself
                    self.world.grid[patch] = self         #update the grid
                    i_moved = True
                    if self.kind == 'red':
                        return 1 #red moved
                    else:
                        return 7 #blue moved
                 #if not i_moved:
            if i_moved is False:
                if self.kind == 'red':
                    return 2 # red failed to move
                else:
                    return 8  # blue failed to move              
        elif happy: 
            if self.kind == 'red':
                return 0 # red happy
            else:
                return 6 # blue happy

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
    
    def start_happy_r_b(self):
    #for reporting purposes, allow count of happy before any moves, of red and blue seperately
        if self.am_i_happy and self.kind == 'red':
            return 'a'
        elif self.am_i_happy and self.kind == 'blue':
            return 'b'
        else:
            pass


class World():
    def __init__(self, params):
        assert(params['world_size'][0] * params['world_size'][1] > params['num_agents']), 'Grid too small for number of agents.'
        self.params = params
        self.reports = {}

        self.grid     = self.build_grid(params['world_size'])
        self.agents   = self.build_agents(params['num_agents'], params['same_pref_r'], params['same_pref_b'])

        self.init_world()


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
        self.reports['red_integration'] =[]
        self.reports['blue_integration'] = []

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
        diff_neighbours_r = []
        diff_neighbours_b = []
        for agent in self.agents:
            diff_neighbors.append(sum(
                    [not a for a in agent.am_i_happy(neighbor_check=True)]
                                ))
        for agent in self.agents:
            if agent.kind == 'red':
                diff_neighbours_r.append(sum(
                    [not a for a in agent.am_i_happy(neighbor_check=True)]
                                ))
        for agent in self.agents:
            if agent.kind == 'blue':
                diff_neighbours_b.append(sum(
                    [not a for a in agent.am_i_happy(neighbor_check=True)]
                                ))
                

        self.reports['integration'].append(round(mean(diff_neighbors), 2))
        self.reports['red_integration'].append(round(mean(diff_neighbours_r), 2))
        self.reports['blue_integration'].append(round(mean(diff_neighbours_b), 2))


    def run(self): 
        #handle the iterations of the model
        log_of_happy = []
        log_of_rand  = []
        log_of_rand_r = []
        log_of_rand_b = []
        log_of_happy_r = []
        log_of_happy_b = []
        log_of_moved_r = []
        log_of_moved_b = []
        log_of_moved = []
        log_of_stay  = []
        log_of_stay_r = []
        log_of_stay_b = []

        self.report_integration()
        log_of_happy.append(sum([a.am_i_happy() for a in self.agents])) #starting happiness
        
        happy_results = [agent.start_happy_r_b() for agent in self.agents]
        log_of_happy_r.append(sum([r == 'a' for r in happy_results])) #starting happiness
        log_of_happy_b.append(sum([r == 'b' for r in happy_results])) #starting happiness
        
        log_of_rand_r.append(0) #no one moved at startup
        log_of_rand_b.append(0) #no one moved at startup        
        
        log_of_moved_r.append(0) #no one moved at startup
        log_of_moved_b.append(0) #no one moved at startup

        log_of_stay_r.append(0) #no one stayed at startup
        log_of_stay_b.append(0) #no one stayed at startup

        for iteration in range(self.params['max_iter']):

            random.shuffle(self.agents) #randomize agents before every iteration
            move_results = [agent.move(params) for agent in self.agents]
            
            self.report_integration()

            num_happy_at_start   =sum([r==0 for r in move_results]) + sum([r==6 for r in move_results])
            num_happy_at_start_r = sum([r==0 for r in move_results])
            num_happy_at_start_b = sum([r==6 for r in move_results])
            num_moved            = sum([r==1 for r in move_results]) + sum([r==7 for r in move_results])
            num_moved_r          = sum([r==1 for r in move_results])
            num_moved_b          = sum([r==7 for r in move_results])
            num_stayed_unhappy   = sum([r==2 for r in move_results]) + sum([r==8 for r in move_results])
            num_stayed_unhappy_r = sum([r==2 for r in move_results])
            num_stayed_unhappy_b = sum([r==8 for r in move_results])
            #num_moved_random     = sum([r==3 for r in move_results]) #outdated
            num_moved_random_r   = sum([r==4 for r in move_results]) 
            num_moved_random_b   = sum([r==5 for r in move_results]) 

            log_of_happy.append(num_happy_at_start)
            
            

            #log_of_rand.append(num_moved_random) #debug
            log_of_rand_r.append(num_moved_random_r)
            log_of_rand_b.append(num_moved_random_b)
            log_of_happy_r.append(num_happy_at_start_r)
            log_of_happy_b.append(num_happy_at_start_b)
            log_of_moved.append(num_moved)
            log_of_moved_r.append(num_moved_r)
            log_of_moved_b.append(num_moved_b)
            log_of_stay .append(num_stayed_unhappy)
            log_of_stay_r.append(num_stayed_unhappy_r)
            log_of_stay_b.append(num_stayed_unhappy_b)

           
            #if log_of_moved[-1] == log_of_stay[-1] == 0: 
            if log_of_happy[-1] == params['num_agents']:
                print('Everyone is happy!  Stopping after iteration {}.'.format(iteration))
                break
            elif log_of_moved[-1] == 0 and log_of_stay[-1] > 0:
                print('Some agents are unhappy, but they cannot find anywhere to move to.  Stopping after iteration {}.'.format(iteration))
                break

        self.reports['log_of_happy']   = log_of_happy
        self.reports['log_of_happy_r'] = log_of_happy_r
        self.reports['log_of_happy_b'] = log_of_happy_b
        self.reports['log_of_rand']    = log_of_rand
        self.reports['log_of_rand_r']  = log_of_rand_r
        self.reports['log_of_rand_b']  = log_of_rand_b
        self.reports['log_of_moved']   = log_of_moved
        self.reports['log_of_moved_r'] = log_of_moved_r
        self.reports['log_of_moved_b'] = log_of_moved_b
        self.reports['log_of_stay']    = log_of_stay
        self.reports['log_of_stay_r']  = log_of_stay_r
        self.reports['log_of_stay_b']  = log_of_stay_b

        self.report(params)

    def report(self, params):
        #report final results after run ends
        reports = self.reports

        if params['print_to_screen']:
            print('\nAll results begin at time=0 and go in order to the end.\n')
            print('The average number of neighbors an agent has not like them:', reports['integration'])
            print('The average number of neighbors a red agent has not like them:', reports['red_integration'])
            print('The average number of neighbors a blue agent has not like them:', reports['blue_integration'])
            print('The number of happy agents:', reports['log_of_happy'])
            print('The number of happy red agents:', reports['log_of_happy_r'])
            print('The number of happy blue agents:', reports['log_of_happy_b'])
            print('The number of red agent moves per turn who checked if they would be happy:', reports['log_of_moved_r'])
            print('The number of blue agent moves per turn who checked if they would be happy:', reports['log_of_moved_b'])
            print('The number of red agent moves per turn who did not check if they would be happy:', reports['log_of_rand_r'])
            print('The number of blue agent moves per turn who did not check if they would be happy:', reports['log_of_rand_b'])
            #print('The number of moves per turn who did not check if they would be happy:', reports['log_of_rand']) #outdated
            print('The number of red agents who failed to find a new home:', reports['log_of_stay_r'])
            print('The number of blue agents who failed to find a new home:', reports['log_of_stay_b'])
            #print('check:',reports['log_of_rand']) #debug

        if params['to_file']:
            out_path = self.params['out_path']
            with open(out_path, 'w') as f:
                headers = 'turn,integration,red_integ,blue_integ,num_happy,num_happy_r,num_happy_b,num_moved_without_look_r,num_moved_without_look_b,num_moved_looked_r,num_moved_looked_b,num_stayed_r,num_stayed_b\n'
                f.write(headers)
                for i in range(len(reports['log_of_happy'])):
                    line = ','.join([str(i),
                                     str(reports['integration'][i]),
                                     str(reports['red_integration'][i]),
                                     str(reports['blue_integration'][i]),
                                     str(reports['log_of_happy'][i]),
                                     str(reports['log_of_happy_r'][i]),
                                     str(reports['log_of_happy_b'][i]),
                                     str(reports['log_of_rand_r'][i]),
                                     str(reports['log_of_rand_b'][i]),
                                     str(reports['log_of_moved_r'][i]),
                                     str(reports['log_of_moved_b'][i]),
                                     str(reports['log_of_stay_r'][i]),
                                     str(reports['log_of_stay_b'][i]),
                                     '\n'
                                     ])
                    f.write(line)
            print('\nResults written to:', out_path)

world = World(params)
world.run()

#some intermediary tests and checks:
#a = 0 #debug
#print(world.agents[a].kind) #debug
#print(world.agents[a].same_pref) #debug

#tests at num_agents=20:
#for i in range(20):
#   print(world.agents[i].kind)
#check success: proportion is working

#for i in range(20):
#   print(world.agents[i].same_pref) 
#check success: pref is working

#for i in range(10):
#   print(world.agents[i].move())

#for i in range(10):
 #  print(world.red_agents[i].kind)

#world.agents[0].kind == 'red'
#world.agents[0].kind == 'red'
#world.agents[0].start_happy_r()
#world.agents[0].start_happy_b()




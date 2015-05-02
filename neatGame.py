__author__ = 'user'
import math
import random
import cPickle as pickle
from neat import config, population, chromosome, genome #visualize
from neat.nn import nn_pure as nn
import neatGame
#from neat.nn import nn_cpp as nn # C++ extension

config.load('game_config')

# set node gene type
chromosome.node_gene_type = genome.NodeGene

# XOR-2
NUMAVG = 10


def eval_fitness(population):

    for chromo in population:
        net = nn.create_ffphenotype(chromo)
        play = neatGame.Game()
        temp = 0.0
        for x in range(NUMAVG):
            temp += play.main_loop(False, net)
        temp = temp / NUMAVG
        chromo.fitness = temp / 10000.0

population.Population.evaluate = eval_fitness

pop = population.Population()
pop.epoch(300, report=True, save_best=False)

winner = pop.stats[0][-1]
print 'Number of evaluations: %d' %winner.id

# Visualize the winner network (requires PyDot)
# visualize.draw_net(winner) # best chromosome

# Plots the evolution of the best/average fitness (requires Biggles)
# visualize.plot_stats(pop.stats)
# Visualizes speciation
# visualize.plot_species(pop.species_log)

# Let's check if it's really solved the problem
print '\nBest network output:'
brain = nn.create_ffphenotype(winner)
neatGame.Game().main_loop(True, brain)


# saves the winner
file = open('winner_chromosome', 'w')
pickle.dump(winner, file)
file.close()

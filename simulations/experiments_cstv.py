"""
An implementation of the algorithms in:
"Participatory Budgeting with Cumulative Votes", by Piotr Skowron, Arkadii Slinko, Stanisaw Szufa, Nimrod Talmon (2020), https://arxiv.org/pdf/2009.02690
Programmer: Achiya Ben Natan
Date: 2024/05/16.
"""

import logging
from pabutools.rules.CSTV import *
from experiments_csv import *
import simulations.helpExp as he
import pandas as pd
import matplotlib.pyplot as plt



def exp_time():
    ex = Experiment("simulations/results","results_time.csv","simulations/backup_results")
    ex.logger.setLevel(logging.CRITICAL)
    ex.clear_previous_results()
    input_ranges = {
        "inputs" : he.create_input_1(),
        "combination": ["ewt", "improved_mt", "old_mt", "ewtc", "improved_mtc", "old_mtc"]
    }
    ex.run(he.cstv_budgeting_combination_exp, input_ranges)
    


def exp_with_variations():
    ex = Experiment("simulations/results", "results_var.csv", "simulations/backup_results")
    ex.logger.setLevel(logging.CRITICAL)
    ex.clear_previous_results()
    input_ranges = {
        "inputs" : he.create_inputs_2(),
        "combination": ["var_ewt", "var_improved_mt", "var_old_mt", "var_ewtc", "var_improved_mtc", "var_old_mtc"]
    }  
    ex.run(he.cstv_budgeting_combination_exp,input_ranges)
    print("exp with variations:\n", ex.dataFrame)
    

def exp_para():
    ex = Experiment("simulations/results", "results_para.csv", "simulations/backup_results")
    ex.logger.setLevel(logging.CRITICAL)
    ex.clear_previous_results()
    projects, donors = he.create_input_3()
    inputs = (copy.deepcopy(projects),copy.deepcopy(donors))
    input_ranges = {
        "inputs" : [inputs],
        "combination": ["improved_mt", "ewt", "old_mt", "ewtc", "improved_mtc", "old_mtc"]
    }
    ex.run(he.calculate_metrics,input_ranges)
    print(ex.dataFrame)


logging.basicConfig(level=logging.INFO)

# exp_time()
# exp_with_variations()
# exp_para()
file_path = 'simulations/results/results_time.csv'
# single_plot_results(file_path, filter={}, x_field="inputs", y_field="time_taken", z_field="combination")
# file_path = 'simulations/results/results_para.csv'
# single_plot_results(file_path, filter={}, x_field="inputs", y_field="Voter Satisfaction", z_field="combination", mean=False)
# single_plot_results(file_path, filter={}, x_field="inputs", y_field="Anger ratio", z_field="combination", mean=False)
# single_plot_results(file_path, filter={}, x_field="inputs", y_field="Avarge cost", z_field="combination", mean=False)
file_path = 'simulations/results/results_var_50.csv'
single_plot_results(file_path, filter={}, x_field="inputs", y_field="time_taken", z_field="combination")
file_path = 'simulations/results/results_var_100.csv'
single_plot_results(file_path, filter={}, x_field="inputs", y_field="time_taken", z_field="combination")
file_path = 'simulations/results/results_var_150.csv'
single_plot_results(file_path, filter={}, x_field="inputs", y_field="time_taken", z_field="combination")


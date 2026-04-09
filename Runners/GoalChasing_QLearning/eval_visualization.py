import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import pandas as pd
import json

from Agents.DQAgent import DQAgent
from Agents.CADRLAgent import CADRLStyleAgent

def get_agent_conf():
    agents_configs = {
        'DQN (Greedy)': DQAgent(
            state_dim,
            action_dim,
            epsilon_decay=0.9998,
            epsilon_min=0.01,
            target_update_freq=1000,
            memory_size=50000,
            batch_size=512
            ),
        'CADRL-Style': CADRLStyleAgent(
            state_dim,
            action_dim,
            epsilon_decay=0.9998,
            epsilon_min=0.01,
            target_update_freq=1000,
            memory_size=50000,
            num_action_samples=8,
            batch_size=512
            )
    }
    return agents_configs

def plot_trials(train_metrics, N=2,name='losses', save: bool | str=False, show=False):
    if show or save:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    for i in range(N):
    
        metric = train_metrics['DQL'] if i == 0 else train_metrics['CADRL']
        metric_name = 'DQL' if i == 0 else 'CADRL'
    
        num_robots = len(metric[name][0])
        cmap = plt.get_cmap('gist_ncar', num_robots)
        cum_sum_range = 0
    
        range_val = len(metric[name])
        range_start = cum_sum_range
        range_end = cum_sum_range + range_val
        cum_sum_range += range_val
        values = np.arange(range_start, range_end)
    
        reward_data = np.zeros((range_val, num_robots))
        for j in range(num_robots):
            agent_name = f'agent{j+1}'
            rewards = [metric[name][k][agent_name] for k in range(range_val)]
            reward_data[:, j] = rewards
            if (N == 1) and (show or save):
                ax.plot(values, rewards, alpha=0.2, color=cmap(j))
    
        # Plot average loss for this batch
        if show or save:
            plt.plot(values, np.mean(reward_data, axis=1), alpha=0.7, color='black' if i == 0 else 'red', label=f'Average {name.capitalize()} - {metric_name}' )
    
    if (N == 1) and (show or save):
        sm = mpl.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(0, num_robots))
        cbar = fig.colorbar(sm, ax=ax, ticks=np.arange(num_robots), label="Robot IDs")
        cbar.ax.tick_params(**map_fonts['cbar_tick']) if 'cbar_tick' in map_fonts else None
        cbar.set_label(f'Average {name.capitalize()}', **map_fonts['cbar_label'])

    if show or save:
        plt.title(f'{name.capitalize()} vs Epoch', fontdict=map_fonts['title'])
        plt.xlabel('Epoch', fontdict=map_fonts['xlabel'])
        plt.ylabel(f'{name.capitalize()}', fontdict=map_fonts['ylabel'])
        plt.xticks(**map_fonts['xtick'])
        plt.yticks(**map_fonts['ytick'])
        plt.legend(**map_fonts['legend'])
        if save:
            plt.savefig(save)
        if show:
            plt.show()

def check_collision(path, show=False):
    with open(path,'r') as f: # DQN_(Greedy) CADRL-Style
        custom_metrics = json.loads(f.read())
    collision_data = [np.array(custom_metrics['collisions'][i]) for i in range(len(custom_metrics['collisions']))]
    mean_collision_rates = []
    for x in collision_data:
        # print(x.shape)
        try:
            x[x==None] = np.nan
            
        except:
            print(x, x.shape)
        mean_collision_rates.append(np.nanmean(x))
    if show:
        plt.figure()
        plt.plot(range(len(collision_data)),mean_collision_rates)
        plt.show()
    return collision_data, mean_collision_rates

state_dim = (2 * 10 + 1) ** 2 * 2 + 2
action_dim = 8

map_fonts = {
   'title' : {'fontsize': 20, 'fontweight': 'bold', 'color': 'black'},
   'xlabel' : {'fontsize': 15, 'fontweight': 'medium', 'color': 'black'},
   'ylabel' : {'fontsize': 15, 'fontweight': 'medium', 'color': 'black'},
   'xtick' : {'fontsize': 12, 'fontweight': 'medium', 'color': 'black'},
   'ytick' : {'fontsize': 12, 'fontweight': 'medium', 'color': 'black'},
   'legend' : {'fontsize': 12, 'loc': 'upper right' },
   'cbar_tick' : {'labelsize': 9, 'size': 5},
   'cbar_label' : {'fontsize': 12, 'fontweight': 'medium', 'color': 'black' },
   'heatmap_annot' : {'fontsize': 18, 'fontweight': 'medium' }
}

curriculum_train_metrics = []
for i in range(1,2):
    train_metrics = {
        'DQL': json.load(open(f'/kaggle/input/datasets/darsh22blc1378/direct-trained-agents/results/DQN_(Greedy)-single_{i}/metrics.json')),
        'CADRL': json.load(open(f'/kaggle/input/datasets/darsh22blc1378/direct-trained-agents/results/CADRL-Style-single_{i}/metrics.json'))
    }
    assert train_metrics['DQL']['rewards'] and train_metrics['CADRL']['rewards'], "Metric Rewards data is empty."
    assert train_metrics['DQL']['losses'] and train_metrics['CADRL']['losses'], "Metric Loss data is empty."
    
    curriculum_train_metrics.append(train_metrics)

metric = curriculum_train_metrics
name = 'DQL'
metric_name = 'rewards'
training_len = len(metric)

fig, ax = plt.subplots(figsize=(10, 8))
cum_range = 0
num_robots = 0
for tr in range(training_len):
    print(tr,training_len)
    curr_tr_range = len(metric[tr][name][metric_name])
    curr_num_robots = len(metric[tr][name][metric_name][0])
    num_robots = max(num_robots,curr_num_robots)
    
    curr_tr_start = cum_range
    curr_tr_end = curr_tr_start + curr_tr_range
    cum_range += curr_tr_range

    epoch_vals = np.arange(curr_tr_start, curr_tr_end)
    metric_data = np.zeros((curr_tr_range, curr_num_robots))
    for j in range(curr_num_robots):
        agent_name = f'agent{j+1}'
        vals = [metric[tr][name][metric_name][k][agent_name] if metric[tr][name][metric_name][k][agent_name] else None for k in range(curr_tr_range) ]
        metric_data[: , j] = vals
        cmap = plt.get_cmap('gist_ncar', num_robots)
        ax.plot(epoch_vals, vals, alpha=0.2, color=cmap(j))
    plt.plot(epoch_vals, np.nanmean(metric_data, axis=1), alpha=0.7, color='black')
    print("mean:",tr,np.nanmean(metric_data))
    
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(0, num_robots))
cbar = fig.colorbar(sm, ax=ax, ticks=np.arange(num_robots), label="Robot IDs")
cbar.ax.tick_params(**map_fonts['cbar_tick']) if 'cbar_tick' in map_fonts else None
cbar.set_label(f'Robot Counts', **map_fonts['cbar_label'])

plt.title(f'{metric_name.capitalize()} vs Epoch', fontdict=map_fonts['title'])
plt.xlabel('Epoch', fontdict=map_fonts['xlabel'])
plt.ylabel(f'{metric_name.capitalize()}', fontdict=map_fonts['ylabel'])
plt.xticks(**map_fonts['xtick'])
plt.yticks(**map_fonts['ytick'])
plt.legend()
plt.show()

curriculum_collision_data = []
for i in range(len(curriculum_train_metrics)):
    print("Curriculum Index:",i+1)
    DQN = check_collision(f'results/DQN_(Greedy)_{i+2}/custom_metrics.json')
    CADRL = check_collision(f'results/CADRL-Style_{i+2}/custom_metrics.json')
    curriculum_collision_data.append({
        'DQN' : DQN,
        'CADRL': CADRL
    })

for i in range(len(curriculum_collision_data)):
    mean_collision_rate_DQN = np.mean(curriculum_collision_data[i]['DQN'][1])
    mean_collision_rate_CADRL = np.nanmean(curriculum_collision_data[i]['CADRL'][1])
    curriculum_collision_data[i]['DQN'] = [*curriculum_collision_data[i]['DQN'], mean_collision_rate_DQN]
    curriculum_collision_data[i]['CADRL'] = [*curriculum_collision_data[i]['CADRL'], mean_collision_rate_CADRL]

for i in range(len(curriculum_collision_data)):
    diff = curriculum_collision_data[i]['DQN'][2] - curriculum_collision_data[i]['CADRL'][2]
    better = ">" if diff > 0 else '<'
    
print(
    "DQN:",f"{curriculum_collision_data[i]['DQN'][2]*100:.2f}",
    "\t",better,
    "\tCADRL:",f"{curriculum_collision_data[i]['CADRL'][2]*100:.2f}", 
    "\t", f"{diff*100:.2f}"
)

name = 'CADRL'
for i in range(2,10):
    epoch = len(curriculum_train_metrics[i-2][name]['rewards'])
    epoch_values = []
    for e in range(epoch):
        rewards_dict = curriculum_train_metrics[i-2][name]['rewards'][e]
        losses_dict = curriculum_train_metrics[i-2][name]['losses'][e]
        epoch_values.append({
            'reward' : np.nanmean([*rewards_dict.values()]),
            'loss' : np.nanmean([*losses_dict.values()])
        })
    print(epoch_values[-1])
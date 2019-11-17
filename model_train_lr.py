import matplotlib.pyplot as plt
import configparser
import multiprocessing
import numpy as np
# import time
import os
import sys
home_dir = os.path.expanduser('~')
sys.path.append(os.path.join(home_dir,'Work_Space/my_module/basic-toolbox/basic_tools'))
import plot_tools

from WavLoc_lr_recommend import WavLoc


def main_sub(i):
	# basic variables
	train_set_dir_base = '../Data/v1/train/record'
	valid_set_dir_base = '../Data/v1/valid/record/'

	model_dir = 'models/lr_recommend'
	rooms = ['Anechoic','A','B','C','D']
	# for tar_room in rooms[1:]:
	tar_room = rooms[i+1]
	model_dir_room = os.path.join(model_dir,'mct_not_{}'.format(tar_room))
	if not os.path.exists(model_dir_room):
		os.makedirs(model_dir_room)

	# filter out tar_room from rooms
	mct_room_filter = lambda room : room != tar_room

	config = configparser.ConfigParser()
	config['model']={'model_dir':model_dir_room,
	                'frame_len':320,
					'overlap_len':160,
	                'filter_len':320,
					'is_use_gtf':False,
					'is_padd':False,
	                'azi_num':37}
	config['train']={'batch_size':128,
	                 'max_epoch':50,
					 'adam_params':'0.001,0.9,0.999,1e-08',# settings recomended
					 'is_print_log':True,
	                 'train_set_dir':';'.join([os.path.join(train_set_dir_base,room)
												 for room in filter(mct_room_filter,rooms)]) ,
	                 'valid_set_dir':';'.join([os.path.join(valid_set_dir_base,room)
												 for room in filter(mct_room_filter,rooms)])}

	config_fpath = os.path.join(model_dir_room,'mct_not_{}.cfg'.format(tar_room))
	with open(config_fpath,'w') as config_file:
	    if config_file is None:
	        raise Exception('fail to create file')
	    config.write(config_file)

	model = WavLoc(config_fpath,gpu_index=0)
	model.train_model()


def multi_test_result_plot():
	reverb_rooms = ['A','B','C','D']
	rmse_results_multi_test = [np.load(os.path.join('models',
													'basic_{}'.format(i),
													'chunk_rmse_multi_test.npy'))
								for i in range(3)]
	mean_std_pairs = [[np.mean(result,axis=0),np.std(result,axis=0)]
						for result in rmse_results_multi_test]
	fig = plot_tools.plot_bar(*mean_std_pairs,
			         		  legend=['run_{}'.format(i) for i in range(3)],
							  xticklabels=reverb_rooms,
							  ylabel='RMSE($^o$)')
	return fig


if __name__ == '__main__':
	pool = multiprocessing.Pool()
	pool.map(main_sub,range(1))

	# fig = multi_test_result_plot()
	# plot_tools.savefig(fig,name='rmse_baic_multi_test')
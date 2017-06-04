__author__ = 'Feng Chen'
from inference_multi_core_main import inference_apdm_format, list_sum, list_dot_scalar, calculate_measures, sliding_window_extract
from log import Log
import os
import time
import pickle
import numpy as np
from SL_inference import *
from hourly_data.DataWrapper import *

 

def generateData(hour,weekday,percent=0.05):
    dw = DataWrapper()
    V, E, Obs, G = dw.get_data_case(hour,weekday)

    Omega = obs_to_omega(Obs)
    sizeE = len(E)
    print sizeE
    #E_X = random.sample(E,int(round(sizeE*percent)))
    E_X = []
    size = int(round(sizeE*percent))
    print size

    while len(E_X)< size:
        all_E = [tuple(e) for e in np.random.permutation(E)]
        for e in all_E:
            source, target = e
            for v1,v2 in E:
                if v2 == source:
                    if e not in E_X:
                        E_X.append(e)
                        break
            break
    print len(E_X)
    if len(E_X) == 0:
        raise Exception('HAHA EMPTY X HERE')

    #print('number of nodes: {}'.format(len(V)))
    #print('number of edges: {}'.format(len(E)))
    #print('number of cc: {}'.format(nx.number_connected_components(G)))
    outfile = open('data/data.pkl','w')
    pickle.dump([V,E,Omega,Obs,E_X],outfile)
    outfile.close()




def single():
    '''
    prediction for one weekday and one hour
    '''
    window_size = 5
    begin_time = 0
    end_time = 44
    logging = Log("log.txt")
    filename = "data/data.pkl"
    if os.path.exists(filename):
        running_starttime = time.time()
        pkl_file = open(filename, 'rb')
        [V, E, Omega, Obs, X] = pickle.load(pkl_file)
        if len(X) == 0:
            raise Exception('EMPTY X 2')
        pkl_file.close()
        logging.write('\r\n\r\nfilename: {0}, #nodes: {1}, #edges: {2}'.format(filename, len(V), len(E)))

        sw_measures = []
        for start_t in range(begin_time, end_time-window_size+1):
            print "sliding window: {0} to {1}".format(start_t, start_t + window_size)
            logging.write("\r\n sliding window: {0} to {1}".format(start_t, start_t + window_size))
            sw_Omega, sw_Obs = sliding_window_extract(Omega, Obs, start_t, window_size)

            if len(X) == 0: 
                raise Exception('EMPTY X')
            X_copy = [e for e in X]
            #pred_omega_x = SL_prediction(V,E,sw_Obs,sw_Omega,X_copy)
            pred_omega_x = inference_apdm_format(V, E, sw_Obs, sw_Omega, X_copy, logging)
            prob_mse, u_mse, prob_relative_mse, u_relative_mse, accuracy, recall_congested, recall_uncongested = calculate_measures(sw_Omega, pred_omega_x, X, logging)
            sw_measures.append([prob_mse, u_mse, prob_relative_mse, u_relative_mse, accuracy, recall_congested, recall_uncongested])

        avg_measures = [0, 0, 0, 0, 0, 0, 0]
        for measures in sw_measures:
            avg_measures = list_sum(avg_measures, measures)
        avg_measures = list_dot_scalar(avg_measures, 1.0 / len(sw_measures))
        logging.write("\r\n ----------------Summary of the results--------------------")
        logging.write("prob_mse: {0}, u_mse: {1}, prob_relative_mse: {2}, u_relative_mse: {3}".format(prob_mse, u_mse, prob_relative_mse, u_relative_mse))
        logging.write("accuracy: {0}, recall_congested: {1}, recall_uncongested: {2}".format(accuracy, recall_congested, recall_uncongested))

        running_endtime = time.time()
        logging.write("\r\n running time: {0} seconds".format(running_endtime - running_starttime))
    return prob_mse, u_mse, prob_relative_mse, u_relative_mse,accuracy, recall_congested, recall_uncongested


if __name__=='__main__':
    #outfile = open('result_csl_summary','w')
    outfile = open('result_sl_summary','w')
    weekday = 0
    for i in range(8,13):
        outfile.write( "File:  weekday {}, hour {}".format(weekday,i))
        start_time = time.time()
        generateData(i,weekday)
        prob_mse, u_mse, prob_relative_mse, u_relative_mse,accuracy, recall_congested, recall_uncongested = single()
        outfile.write("\r\n ----------------Summary of the results--------------------\n")
        outfile.write("prob_mse: {0},\n u_mse: {1},\n prob_relative_mse: {2},\n u_relative_mse: {3}\n".format(prob_mse, u_mse, prob_relative_mse, u_relative_mse))
        outfile.write("accuracy: {0},\n recall_congested: {1},\n recall_uncongested: {2}\n".format(accuracy, recall_congested, recall_uncongested))

        end_time = time.time()
        outfile.write('processing time {}'.format(end_time-start_time))
    outfile.close()



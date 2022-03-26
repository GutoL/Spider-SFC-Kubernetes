import sys

from matplotlib.pyplot import plot

from calc_communication_delay import generate_results_without_src_dst
from calc_vnf_processing_time import generate_results


if __name__ == "__main__":

    if len(sys.argv) > 1:
        name_file = sys.argv[1]
        content = name_file.split('/')

        if 'without' in content[0]:
            with_src_dst = False
        else:
            with_src_dst = True

    else:
        print('Please, provide the file name')
        sys.exit()
    
    f = open(name_file,'r')

    lines = f.readlines()

    f.close()
    number_of_experiments = 30

    if with_src_dst == False:
        number_of_info_per_experiment = 4
        number_of_vnfs = 3 # compress image, firewall, face detection
        
        communication_data = generate_results_without_src_dst(number_of_vnfs, number_of_experiments, number_of_info_per_experiment, lines)
        
        f = open('without_src_dst/delay_results_3_vnfs_with_delay.txt','r')
        lines = f.readlines()
        f.close()
        processing_data = generate_results(number_of_experiments, number_of_info_per_experiment, lines, with_src_dst, plot=False)

        communication_delay = communication_data[0].mean()
        print('communication delay:',communication_delay)

        vnfs_names = list(processing_data['VNF Name'].value_counts().keys())
        total_vnf_processing_delay = 0
        
        # calculating overall delay
        for vnf in vnfs_names:
            vnf_delay = processing_data[processing_data['VNF Name']==vnf]['Runtime (in seconds)'].mean()
            print(vnf,'delay:', vnf_delay)
            total_vnf_processing_delay += vnf_delay
        
        print('VNF processing delay:',total_vnf_processing_delay)

        overall_delay = communication_delay + total_vnf_processing_delay
        print('-----------------------\nOverall SFC delay:',overall_delay)

        print('Communication delay impact:',(communication_delay*100)/overall_delay)
        print('VNF processing delay impact:',(total_vnf_processing_delay*100)/overall_delay)
        
        




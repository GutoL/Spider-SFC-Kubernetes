import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from calc_e2e_delay import get_times_per_vnf

def get_processing_time(vnf_name, vnf_t1, vnf_t2, dictionary):
    
    if vnf_name not in dictionary:
        dictionary[vnf_name] = [(vnf_t2-vnf_t1).total_seconds()]
    else:
        dictionary[vnf_name].append((vnf_t2-vnf_t1).total_seconds())

    return dictionary

def generate_box_plot(processing_time_per_vnf):

    columns_name = ['VNF Name','Runtime (in seconds)']
    df = pd.DataFrame(columns=columns_name)
    
    for vnf in processing_time_per_vnf:
        temp_df = pd.DataFrame([(vnf,runtime) for runtime in processing_time_per_vnf[vnf]], columns=columns_name)
        df = pd.concat([df, temp_df])

    vnf_name_replace = {
        'my-sfc-compress-image':'Compress Image',
        'my-sfc-firewall': 'Firewall',
        'my-sfc-face-detection': 'Face Detection'
    }

    vnf_name = 'my-sfc-compress-image'
    print(vnf_name+':\n', df[df['VNF Name'] == vnf_name].describe())
    df['VNF Name'].replace(vnf_name, vnf_name_replace[vnf_name], inplace=True)

    vnf_name = 'my-sfc-firewall'
    print(vnf_name+':\n', df[df['VNF Name'] == vnf_name].describe())
    df['VNF Name'].replace(vnf_name, vnf_name_replace[vnf_name], inplace=True)

    vnf_name = 'my-sfc-face-detection'
    print(vnf_name+':\n',df[df['VNF Name'] == vnf_name].describe())
    df['VNF Name'].replace(vnf_name, vnf_name_replace[vnf_name], inplace=True)

    sns.boxplot(x=df[columns_name[0]],y=df[columns_name[1]], palette="Blues", width=0.5)
    plt.show()   

def generate_results(number_of_experiments, number_of_info_per_experiment, lines):
    processing_time_per_vnf = {}

    for x in range(number_of_experiments):
        i = x*number_of_info_per_experiment
        _, vnf3, vnf2, vnf1 = lines[i:i+number_of_info_per_experiment]

        vnf1_name, vnf1_t1, vnf1_t2 = get_times_per_vnf(vnf1)
        vnf2_name, vnf2_t1, vnf2_t2 = get_times_per_vnf(vnf2)
        vnf3_name, vnf3_t1, vnf3_t2 = get_times_per_vnf(vnf3)

        processing_time_per_vnf = get_processing_time(vnf1_name, vnf1_t1, vnf1_t2, processing_time_per_vnf)
        processing_time_per_vnf = get_processing_time(vnf2_name, vnf2_t1, vnf2_t2, processing_time_per_vnf)
        processing_time_per_vnf = get_processing_time(vnf3_name, vnf3_t1, vnf3_t2, processing_time_per_vnf)
    
    generate_box_plot(processing_time_per_vnf)

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
    number_of_experiments = 30

    if with_src_dst == True:
        number_of_info_per_experiment = 6
        number_of_vnfs = 5 # source, compress image, firewall, face detection, destination
        generate_results(number_of_experiments, number_of_info_per_experiment, lines)

    elif with_src_dst == False:
        number_of_info_per_experiment = 4
        number_of_vnfs = 3 # compress image, firewall, face detection
        generate_results(number_of_experiments, number_of_info_per_experiment, lines)
    

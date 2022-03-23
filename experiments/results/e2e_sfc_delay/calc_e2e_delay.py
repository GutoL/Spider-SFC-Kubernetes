import datetime
import pandas as pd
import sys


# Function to convert string to datetime
def convert(date_time):
    date_time = date_time.strip()

    format = '%Y-%m-%d %H:%M:%S.%f' # The format
    datetime_str = datetime.datetime.strptime(date_time, format)
   
    return datetime_str

def get_times_per_vnf(log_vnf):
    split_index = log_vnf.find(':')

    vnf_name = log_vnf[0:split_index]
    time1, time2 = log_vnf[split_index+1:len(log_vnf)].split(',')
    
    return vnf_name, convert(time1), convert(time2)

def generate_results_with_src_dst(number_of_vnfs, number_of_experiments, number_of_info_per_experiment, lines):
    
    delay_between_vnfs = {x: [] for x in range(number_of_vnfs-1)} # number of flow entries: n° of VNFs-1
    sfc_overall_delay_list = []

    for x in range(number_of_experiments):
        i = x*number_of_info_per_experiment

        _, destination, vnf3, vnf2, vnf1, source = lines[i:i+number_of_info_per_experiment]

        source_name, source_t1, source_t2 = get_times_per_vnf(source)
        vnf1_name, vnf1_t1, vnf1_t2 = get_times_per_vnf(vnf1)
        vnf2_name, vnf2_t1, vnf2_t2 = get_times_per_vnf(vnf2)
        vnf3_name, vnf3_t1, vnf3_t2 = get_times_per_vnf(vnf3)
        destination_name, destination_t1, destination_t2 = get_times_per_vnf(destination)

        sfc_overall_delay = 0

        t1 = (vnf1_t1-source_t2).total_seconds()
        delay_between_vnfs[0].append(t1) # source -> compress image
        sfc_overall_delay += t1

        t1 = (vnf2_t1-vnf1_t2).total_seconds()
        delay_between_vnfs[1].append(t1) # compress image -> firewall
        sfc_overall_delay += t1

        t1 = (vnf3_t1-vnf2_t2).total_seconds()
        delay_between_vnfs[2].append(t1) # firewall -> face detection
        sfc_overall_delay += t1

        t1 = (destination_t1-vnf3_t2).total_seconds()
        delay_between_vnfs[3].append(t1) # face detection -> destination
        sfc_overall_delay += t1

        sfc_overall_delay_list.append(sfc_overall_delay)

        # print(source_name,'->',vnf1_name,':',vnf1_t1-source_t2)
        # print(vnf1_name,'->',vnf2_name,':',vnf2_t1-vnf1_t2)
        # print(vnf2_name,'->',vnf3_name,':',vnf3_t1-vnf2_t2)
        # print(vnf3_name, '->',destination_name,':',destination_t1-vnf3_t2)
        # print('-------')

    data = pd.DataFrame(sfc_overall_delay_list)
    print(data.describe())
    
    
    # for x in delay_between_vnfs:
    #     print(np.mean(delay_between_vnfs[x]))

def generate_results_without_src_dst(number_of_vnfs, number_of_experiments, number_of_info_per_experiment, lines):
    
    delay_between_vnfs = {x: [] for x in range(number_of_vnfs-1)} # number of flow entries: n° of VNFs-1
    sfc_overall_delay_list = []

    for x in range(number_of_experiments):
        i = x*number_of_info_per_experiment
        _, vnf3, vnf2, vnf1 = lines[i:i+number_of_info_per_experiment]

        vnf1_name, vnf1_t1, vnf1_t2 = get_times_per_vnf(vnf1)
        vnf2_name, vnf2_t1, vnf2_t2 = get_times_per_vnf(vnf2)
        vnf3_name, vnf3_t1, vnf3_t2 = get_times_per_vnf(vnf3)

        # print(vnf1_name,'->',vnf2_name,':',vnf2_t1-vnf1_t2)
        # print(vnf2_name,'->',vnf3_name,':',vnf3_t1-vnf2_t2)
        # print('-------')

        sfc_overall_delay = 0

        t1 = (vnf2_t1-vnf1_t2).total_seconds()
        delay_between_vnfs[0].append(t1) # compress image -> firewall
        sfc_overall_delay += t1

        t1 = (vnf3_t1-vnf2_t2).total_seconds()
        delay_between_vnfs[1].append(t1) # firewall -> face detection
        sfc_overall_delay += t1

        sfc_overall_delay_list.append(sfc_overall_delay)
    
    data = pd.DataFrame(sfc_overall_delay_list)
    print(data.describe())

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
        generate_results_with_src_dst(number_of_vnfs, number_of_experiments, number_of_info_per_experiment, lines)
    
    elif with_src_dst == False:
        number_of_info_per_experiment = 4
        number_of_vnfs = 3 # compress image, firewall, face detection
        generate_results_without_src_dst(number_of_vnfs, number_of_experiments, number_of_info_per_experiment, lines)
    

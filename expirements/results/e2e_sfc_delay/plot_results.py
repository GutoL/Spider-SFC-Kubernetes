import datetime

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

if __name__ == "__main__":
    f = open('delay_results_3_vnfs_with_delay.txt','r')

    lines = f.readlines()
    number_of_experiments = 30
    number_of_info_per_experiment = 4

    delay_per_vnf = {}

    for x in range(number_of_experiments):
        i = x*number_of_info_per_experiment

        _, vnf3, vnf2, vnf1 = lines[i:i+number_of_info_per_experiment]

        vnf1_name, vnf1_t1, vnf1_t2 = get_times_per_vnf(vnf1)
        vnf2_name, vnf2_t1, vnf2_t2 = get_times_per_vnf(vnf2)
        vnf3_name, vnf3_t1, vnf3_t2 = get_times_per_vnf(vnf3)

        print(vnf1_name,'->',vnf2_name,':',vnf2_t1-vnf1_t2)
        print(vnf2_name,'->',vnf3_name,':',vnf3_t1-vnf2_t2)
        print('-------')


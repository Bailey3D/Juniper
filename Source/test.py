import juniper.utilities.network


for i in range(20):
    print(juniper.utilities.network.ping("www.google.com", timeout=1))
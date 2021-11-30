import requests
import pandas as pd
import django
import os
from datetime import datetime
os.environ['DJANGO_SETTINGS_MODULE'] = 'dashboard.settings'  # configure()
django.setup()
from main.models import *
data = pd.read_excel('data.xlsx')

# print(requests.get("http://api.geonames.org/countryCodeJSON?lat=45.96&lng=0.86&username=avishekexe").json())
def add_data():
    data = pd.read_excel('ping_data.xlsx')
    data_list = []
    PingData.objects.all().delete()
    code_wise_country = {i.code_2: i for i in Country.objects.all()}

    for i in data.index:

        obj = PingData()
        obj.lat = data['Latitude'][i]
        obj.long = data['Longitude'][i]
        obj.country = code_wise_country.get(data['Country'][i])
        obj.ping_time = data['Ping'][i]
        obj.connection_type = data['ConnectionType'][i]
        obj.web_link = data['Website'][i]
        obj.network = data['Network'][i]
        obj.provider = data['Cloudp'][i]

        a = data['TestDateTime'][i]
        a = a.split("(")[1].split("+")[0]
        obj.test_time = datetime.utcfromtimestamp(int(a)/1000)
        data_list.append(obj)
    PingData.objects.bulk_create(data_list)

def add_countries():
    con = pd.read_excel('country.xlsx')
    country_list = []
    for i in con.index:
        print(con['country'][i], con['code_2'][i], con['code_3'][i],con['color'][i])
        con_obj = Country()
        con_obj.name = con['country'][i]
        con_obj.code_2 = con['code_2'][i]
        con_obj.code_3 = con['code_3'][i]
        con_obj.color = con['color'][i]
        country_list.append(con_obj)

    Country.objects.bulk_create(country_list)

def add_master_data():
    MasterData.objects.all().delete()
    df = pd.read_excel('master_data.xlsx')
    datalist = []
    code_wise_country_obj = {i.code_2: i for i in Country.objects.all()}
    for i in df.index:
        mas_obj = MasterData()
        mas_obj.country = code_wise_country_obj.get(df['code'][i])
        mas_obj.national = df['National'][i]
        mas_obj.intra = df['INTRA EU'][i]
        mas_obj.data_gb_per_month = df['Data GB/m'][i]
        mas_obj.extra = df['EXTRA EU'][i]
        datalist.append(mas_obj)
    MasterData.objects.bulk_create(datalist)

def add_internet_data_flow_data():
    InternetDataFlow.objects.all().delete()
    df = pd.read_excel('Data_Flow_by_Country.xlsx')
    code_wise_country_obj = {i.code_2: i for i in Country.objects.all()}
    country_code = list(df.columns)[2:]
    print(country_code)
    for i in country_code:
        print(code_wise_country_obj.get(i).name)
    final_data = []
    for i in df.index:
        for con in country_code:
            obj = InternetDataFlow()
            obj.country = code_wise_country_obj.get(con)
            obj.at_time = df['time'][i]
            obj.gb_per_sec = df[con][i]
            final_data.append(obj)
    InternetDataFlow.objects.bulk_create(final_data)

def dataflow_matrix():
    df = pd.read_excel('Data Flow Matrix.xlsx')

    DataFlowMatrixCountry.objects.all().delete()
    DataFlowMatrix.objects.all().delete()
    for i in df.columns[1:]:
        try:
            obj= Country.objects.get(code_2=i)
            DataFlowMatrixCountry.objects.get_or_create(country=obj)
        except:
            obj,st = Country.objects.get_or_create(name=i, code_3=i, code_2=i)
            DataFlowMatrixCountry.objects.get_or_create(country=obj)
    dat_con = {i.country.code_2: i for i in DataFlowMatrixCountry.objects.select_related('country').all()}
    country_obj = {i.code_2: i for i in Country.objects.all()}
    data_list = []

    for i in df.columns[1:]:
        dat_country_obj = dat_con.get(i)
        for dat in df.index:
            obj = DataFlowMatrix()
            obj.from_country = dat_country_obj
            obj.to_country = country_obj.get(df['country'][dat])
            obj.data_gb_per_month = df[i][dat]
            data_list.append(obj)

    DataFlowMatrix.objects.bulk_create(data_list)





if __name__ == '__main__':
    print('Working')
    import pandas as pd

    # dataflow_matrix()
    # add_master_data()
    # print(MasterData.objects.count())
    # add_internet_data_flow_data()
    # c_obj = Country.objects.get(code_2="AL")
    # print(c_obj.id)
    # for i in DataFlowMatrixCountry.objects.filter(country__code_2='BE'):
    #     print(i.country.code_2)
    # for i in DataFlowMatrix.objects.filter(from_country__country__code_2='BE'):
    #     print(i.to_country.code_2)
    # for i in PingData.objects.filter(country__code_2='UK'):
    #     i.country = c_obj
    #     i.save()

    # df1.to_excel('new_test.xlsx')


    # for i in pre_data.index:
    #     data = {}
    #     if str(pre_data['Product Codes'][i]).__contains__(","):
    #         for pr in pre_data['Product Codes'][i].split(","):
    #             data = get_current_index_data(index=i, product_code=pr.replace("\t", '').replace('\n', ''))
    #             data_list.append(data)
    #     elif str(pre_data['Product Codes'][i]).__contains__("\n"):
    #         for pr in pre_data['Product Codes'][i].split("\n"):
    #             data = get_current_index_data(index=i, product_code=pr.replace("\t", '').replace('\n', ''))
    #             data_list.append(data)
    #     else:
    #         data = get_current_index_data(index=i, product_code=pre_data['Product Codes'][i])
    #         data_list.append(data)
    #
    # df = pd.DataFrame(data_list)
    # df.to_excel("testt.xlsx")





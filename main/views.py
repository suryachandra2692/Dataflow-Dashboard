from django.shortcuts import render
from .models import *
from django.db.models import Count
import pandas as pd

from .analysis import dataflow
from .analysis import pingdata


# Create your views here.


def dashboard(request):
    data = {}
    data['country'] = PingData.objects.select_related('country').values('country__code_2').distinct().count()
    data['ping_time'] = PingData.objects.values('ping_time').count()
    data['web_link'] = PingData.objects.values('web_link').distinct().count()
    data['network'] = PingData.objects.values('network').distinct().count()
    # Collecting Data For Map
    country_code_wise_obj = {}
    for i in PingData.objects.select_related('country').all().order_by('test_time'):
        if i.country.name not in country_code_wise_obj.keys():
            country_code_wise_obj[i.country.name] = [i]
        else:
            country_code_wise_obj[i.country.name].append(i)
    data['country_vs_ping'] = get_map_data(country_wise_ping_list=country_code_wise_obj)
    data['urls_list'] = PingData.objects.values('web_link').annotate(count=Count('ping_time'))
    data['total_national_reading'] = 0.0
    data['total_intra_reading'] = 0.0
    data['total_extra_reading'] = 0.0
    for i in MasterData.objects.all():
        data['total_national_reading'] += i.national
        data['total_intra_reading'] += i.intra
        data['total_extra_reading'] += i.extra
    data_flow_obj = InternetDataFlow.objects.select_related('country').all()
    data['country_vs_exchange'] = [[i.country.name, i.gb_per_sec]
                                   for index, i in enumerate(data_flow_obj.filter(at_time=192))
                                   if i.country is not None
                                   ]

    master_data = MasterData.objects.select_related('country').all()
    data['labels'] = [i.country.name for i in master_data if i.country is not None]
    data['national'] = [round(i.national / i.data_gb_per_month * 100, 2) for i in master_data]
    data['intra'] = [round(i.intra / i.data_gb_per_month * 100, 2) for i in master_data]
    data['extra'] = [round(i.extra / i.data_gb_per_month * 100, 2) for i in master_data]

    data['data1'] = []
    all_hours = list(set([i.at_time for i in InternetDataFlow.objects.all().order_by('at_time')]))
    all_data = InternetDataFlow.objects.select_related('country').all().order_by('country__name')
    for i in all_hours:
        dat = {}
        dat['at_time'] = i
        dat['country_data'] = {}
        for country in all_data.filter(at_time=i):
            dat['country_data'].update({country.country.name: country.gb_per_sec})
        data['data1'].append(dat)
    data['all_country'] = list(set([i.country.name for i in all_data]))
    return render(request, 'dashboard.html', data)


def visualization(request):
    search_param = {}
    fil = {}
    if 'country_code' in request.GET.keys():
        country = request.GET.get('country_code')
    else:
        country = 'FR'
    search_param['country__code_2'] = country
    if 'provider' in request.GET.keys() and request.GET.get('provider') != "":
        provider = request.GET.get('provider')
        search_param['provider'] = provider
        fil['provider'] = provider
    else:
        provider = ''

    data = {}
    data['providers'] = PingData.objects.values('provider').all().distinct()
    selected_data = PingData.objects.select_related('country').filter(**search_param).order_by('test_time')
    data['selected_provider'] = provider
    if len(selected_data) > 0:
        data['selected_data'] = selected_data
        data['latest_ping'] = selected_data[0].ping_time
        data['7_day_avg'] = 0
        if len(selected_data) >= 7:
            selected_data = selected_data[0:8]
        else:
            pass
        for i in selected_data:
            data['7_day_avg'] += int(i.ping_time)
        data['7_day_avg'] /= len(selected_data)
        data['7_day_avg'] = round(data['7_day_avg'], 2)
        data['selected_7_day_data'] = selected_data
        data['country'] = selected_data[0].country.name
    else:
        data['7_day_avg'] = "Sorry Ping Not Found"
        data['latest_ping'] = "Sorry Ping Not Found"
        data['country'] = country

    # Collecting Data For Map
    country_code_wise_obj = {}
    for i in PingData.objects.select_related('country').filter(**fil).order_by('test_time'):
        if i.country.name not in country_code_wise_obj.keys():
            country_code_wise_obj[i.country.name] = [i]
        else:
            country_code_wise_obj[i.country.name].append(i)
    data['country_vs_ping'] = get_map_data(country_wise_ping_list=country_code_wise_obj)
    return render(request, 'visual.html', data)


def data_flow_visualization(request):
    search_param = {}
    fil = {}
    if 'country_code' in request.GET.keys():
        country = request.GET.get('country_code')
    else:
        country = 'FR'
    # search_param['country__code_2'] = country
    if 'in_hours' in request.GET.keys() and request.GET.get('in_hours') != "":
        times = request.GET.get('in_hours')
        search_param['at_time'] = times
    else:
        times = 24
    data = {}
    data_flow_obj = InternetDataFlow.objects.select_related('country').all()
    filtered_obj = data_flow_obj.filter(**search_param).order_by('country__name')
    all_hours = list(set([i.at_time for i in InternetDataFlow.objects.all().order_by('at_time')]))
    data['hours'] = all_hours
    data['selected_hour'] = int(request.GET.get('in_hours'))
    data['country_vs_ping'] = [[i.country.name, i.gb_per_sec]
                               for index, i in enumerate(data_flow_obj.filter(at_time=times))
                               if i.country is not None
                               ]
    clicked_region = data_flow_obj.filter(country__code_2=country)
    try:
        data['country'] = clicked_region.get(at_time=times).country.name
    except:
        data['country'] = country
    try:
        current_region_with_time = clicked_region.get(at_time=times).gb_per_sec
    except:
        current_region_with_time = 0.0
    data['table_data'] = []
    for i in filtered_obj:
        dat = {}
        dat['country'] = i.country.name if i.country is not None else i.id
        dat['gb_per_sec'] = i.gb_per_sec
        dat['at_time'] = i.at_time
        dat['status'] = 'D'
        dat['variance'] = 0
        if current_region_with_time < i.gb_per_sec:
            dat['status'] = 'U'
            dat['variance'] = i.gb_per_sec - current_region_with_time
        else:
            dat['status'] = 'D'
            dat['variance'] = current_region_with_time - i.gb_per_sec
        data['table_data'].append(dat)
    try:
        data['last_data_flow'] = round(clicked_region.last().gb_per_sec, 3)
    except:
        data['last_data_flow'] = 0.0
    data['avg_data_flow'] = 0.0
    for i in clicked_region:
        data['avg_data_flow'] += i.gb_per_sec
    try:
        data['avg_data_flow'] /= len(clicked_region)
        data['avg_data_flow'] = round(data['avg_data_flow'], 3)
    except:
        data['avg_data_flow'] = 0.0
    return render(request, 'data_flow_visualisation.html', data)


def internet_data_flow_table(request):
    data = {}
    data['data'] = []
    all_hours = list(set([i.at_time for i in InternetDataFlow.objects.all().order_by('at_time')]))
    all_data = InternetDataFlow.objects.select_related('country').all().order_by('country__name')
    for i in all_hours:
        dat = {}
        dat['at_time'] = i
        dat['country_data'] = {}
        for country in all_data.filter(at_time=i):
            dat['country_data'].update({country.country.name: country.gb_per_sec})
        data['data'].append(dat)
    data['all_country'] = list(set([i.country.name for i in all_data]))
    return render(request, 'internet_data_flow_table.html', data)


def get_map_data(country_wise_ping_list=None):
    datalist = []
    for index, i in enumerate(country_wise_ping_list.keys()):
        data = []
        data.insert(0, i)
        tooltip = get_map_tip_data(country_wise_ping_list[i])
        data.insert(1, (index + 1) * 30)
        data.insert(2, tooltip)
        datalist.append(data)
    return datalist


def get_7_day_avg(data_obj):
    avg = 0.0
    if len(data_obj) >= 7:
        data_obj = data_obj[0:8]
    else:
        pass
    for i in data_obj:
        avg += int(i.ping_time)
    avg /= len(data_obj)
    return round(avg, 2)


def get_recent_ping(data_obj):
    if len(data_obj) > 0:
        return "{0} at ({1})".format(data_obj[0].ping_time, data_obj[0].test_time.strftime("%d %B, %Y %I:%M %p"))
    else:
        return 'No Ping Yet'


def get_master_data_percentages(master_data, country_obj):
    pass


def get_map_tip_data(data_obj):
    last_7_days = get_7_day_avg(data_obj)
    recent_ping = get_recent_ping(data_obj)
    tip = """
        <div class="card shadow mb-4" style="width:250px">
            <div class="card-body">
                <h6>Recent Ping</h6>
                <p style="font-size:14px">{0}</p>
                <h6>Last 7 Days Avg</h6>
                <p style="font-size:14px">{1}</p>
            </div>
        </div>
    """.format(recent_ping, last_7_days)
    return tip


def all_pings(request):
    data = {}
    data['ping_records'] = PingData.objects.select_related('country').all()
    return render(request, 'all_records.html', data)


def all_master_data(request):
    data = {}
    master_data = MasterData.objects.select_related('country').all()
    data['master_data'] = master_data
    return render(request, 'master_data.html', data)


def european_data_flow_data(request):
    data = {}
    data['data_set'] = {}
    for i in DataFlowMatrix.objects.select_related('from_country__country', 'to_country').all().order_by(
            'to_country__name'):
        if i.from_country.country.name not in data['data_set'].keys() and i.from_country is not None:
            data['data_set'][i.from_country.country.name] = {i.to_country.name: i.data_gb_per_month}
        else:
            if i.from_country is not None:
                data['data_set'][i.from_country.country.name].update({i.to_country.name: i.data_gb_per_month})
    data['country_list'] = sorted(list(set(data['data_set'].keys())))
    return render(request, 'european_data_flow_data.html', data)


def get_european_map_data(country_wise_ping_list, master_obj):
    datalist = []
    for index, i in enumerate(country_wise_ping_list.keys()):
        data = []
        data.insert(0, i)
        tooltip = get_map_tip_european_data_flow_visualisation(country_wise_ping_list[i], master_obj)
        data.insert(1, (index + 1) * 30)
        data.insert(2, tooltip)
        datalist.append(data)
    return datalist


def get_mast_info(master_obj, for_country):
    ret = {'national': 0.0, 'intra': 0.0, 'extra': 0.0}

    try:
        print("========", for_country[0].country.code_2)
        if for_country[0].country.code_2 == 'BE':
            print(master_obj.get(for_country[0].country.code_2).national)
        mas = master_obj.get(for_country[0].country.code_2)
        ret['national'] = round(mas.national / mas.data_gb_per_month * 100, 2)
        ret['intra'] = round(mas.intra / mas.data_gb_per_month * 100, 2)
        ret['extra'] = round(mas.extra / mas.data_gb_per_month * 100, 2)

    except Exception as e:
        print(e)
        pass
    return ret


def get_map_tip_european_data_flow_visualisation(country_obj, master_obj):
    print(country_obj[0].country.code_2, "+++++++++++++")
    master_info = get_mast_info(master_obj, country_obj)
    tip = """
            <div class="card shadow mb-4" style="width:250px">
                <div class="card-body">
                    <h6>National</h6>
                    <p style="font-size:14px">{0} %</p>
                    <h6>Intra</h6>
                    <p style="font-size:14px">{1} %</p>
                    <h6>Extra</h6>
                    <p style="font-size:14px">{2} %</p>
                </div>
            </div>
        """.format(master_info.get('national'), master_info.get('intra'), master_info.get('extra'))
    return tip


def european_data_flow_visualisation(request):
    data = {}
    if 'country_code' in request.GET.keys():
        country = request.GET['country_code']
    else:
        country = 'FR'
    country_code_wise_obj = {}
    for i in DataFlowMatrixCountry.objects.select_related('country').all():
        if i.country.name not in country_code_wise_obj.keys():
            country_code_wise_obj[i.country.name] = [i]
        else:
            country_code_wise_obj[i.country.name].append(i)
    country_wise_master_data = {i.country.code_2: i for i in MasterData.objects.select_related('country').all()}
    print(country_wise_master_data.keys())
    data['country_vs_ping'] = get_european_map_data(
        country_wise_ping_list=country_code_wise_obj,
        master_obj=country_wise_master_data
    )
    data['country'] = Country.objects.get(code_2=country).name

    data['matrix'] = DataFlowMatrix.objects.select_related('from_country__country', 'to_country').filter(
        from_country__country__code_2=country)
    return render(request, 'european_data_flow_visualisation.html', data)


def data_flow_geography(request):
    data = {}
    master_data = MasterData.objects.select_related('country').all()
    data['labels'] = [i.country.name for i in master_data if i.country is not None]
    data['national'] = [round(i.national / i.data_gb_per_month * 100, 2) for i in master_data]
    data['intra'] = [round(i.intra / i.data_gb_per_month * 100, 2) for i in master_data]
    data['extra'] = [round(i.extra / i.data_gb_per_month * 100, 2) for i in master_data]
    data['master_data'] = []
    for i in master_data:
        dat = {}
        dat['country_name'] = i.country.name if i.country is not None else i.country
        dat['country_code'] = i.country.code_2 if i.country is not None else i.country
        dat['national'] = round(i.national / i.data_gb_per_month * 100, 2)
        dat['intra'] = round(i.intra / i.data_gb_per_month * 100, 2)
        dat['extra'] = round(i.extra / i.data_gb_per_month * 100, 2)
        data['master_data'].append(dat)
    return render(request, 'visualize_master_data.html', data)


def youth_pop_gdp(request):
    return render(request, 'youth_pop_gdp.html', {})


def rural_vs_urban(request):
    return render(request, 'rural_vs_urban.html', {})


def good_health(request):
    return render(request, 'good_health.html', {})


def tourism(request):
    return render(request, 'tourism.html', {})


def exports_in_eu(request):
    return render(request, 'exports_in_eu.html', {})


def enrollments(request):
    return render(request, 'enrollments.html', {})


def youth(request):
    return render(request, 'youth.html', {})


def independent_data(request):
    data1 = {}
    data1['df'] = pd.read_excel('Independent.xlsx')
    return render(request, 'independent_data.html', data1)


def do_plot_regression():
    p = dataflow.RegressionPlot()
    p.plot_electricity_consumption('assets/img/data-flow-vs-electricity.png')
    p.plot_labour_force('assets/img/data-flow-vs-labour-force.png')
    p.plot_numcars('assets/img/data-flow-vs-cars.png')


def dataflow_regress(request):
    dataflow.plot_correlations('assets/img/dataflow-influencing-vars.png')
    data = {}
    relations = dataflow.get_relations()
    data['relations'] = {i[0]: i[1] for i in relations.to_dict('record')}
    influencing_vars = dataflow.get_influencing_vars()
    data['influencing_vars'] = {i[0]: i[1] for i in influencing_vars.to_dict('record')}
    do_plot_regression()
    return render(request, 'data_flow_regression.html', data)


def ping_data_analysis(request):
    pingdata.plot_ping_by_country('assets/img/ping-by-country.png')
    pingdata.plot_ping_by_provider_country('assets/img/ping-by-country-provider.png')
    pingdata.plot_ping_per_provider('assets/img/ping-by-provider.png')
    data = {}
    return render(request, 'ping_data_analysis.html', data)

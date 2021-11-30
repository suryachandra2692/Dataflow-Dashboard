from main.views import *
from django.urls import path, include

urlpatterns = [
    path('', dashboard),
    path('ping-visualisation', visualization),
    path('all-records', all_pings),
    path('master-data', all_master_data),
    path('visualize-master-data', data_flow_geography),
    path('visualize-data-flow', data_flow_visualization),
    path('internet-exchange-data', internet_data_flow_table),
    path('european-data-flow-data', european_data_flow_data),
    path('european-data-flow-visualisation', european_data_flow_visualisation),
    path('youth-population-and-gdp', youth_pop_gdp),
    path('rural-vs-urban', rural_vs_urban),
    path('tourism', tourism),
    path('good-health', good_health),
    path('enrollments', enrollments),
    path('exports-in-eu', exports_in_eu),
    path('youth-pop', youth),
    path('independent-data', independent_data),
    path('independent-data', independent_data),
    path('data-flow-regression', dataflow_regress),
    path('ping-data-analysis', ping_data_analysis),

]

from django.contrib import admin

# Register your models here.
from main.models import *


class CountryAdmin(admin.ModelAdmin):

    list_display = ['name', 'code_2', 'code_2', 'color']


class PingDataAdmin(admin.ModelAdmin):

    list_display = ['country_name',
                    'country_code_2',
                    'lat',
                    'long',
                    'ping_time',
                    'network',
                    'provider',
                    'test_time',
                    'created_at'
                    ]

    def country_name(self,obj):
        try:
            return obj.country.name
        except:
            return obj.country

    def country_code_2(self,obj):
        try:
            return obj.country.code_2
        except:
            return obj.country


class MasterDataAdmin(admin.ModelAdmin):

    list_display = ['country_name', 'national', 'intra', 'extra', 'data_gb_per_month', 'created_at']

    def country_name(self, obj):
        try:
            return obj.country.name
        except:
            return obj.country

    def country_code_2(self, obj):
        return obj.country.code_2

class DataFlowAdmin(admin.ModelAdmin):

    list_display = ['country_name', 'at_time']

    def country_name(self, obj):
        try:
            return obj.country.name
        except:
            return obj.country

    def country_code_2(self, obj):
        return obj.country.code_2


class DataFlowMatrixAdmin(admin.ModelAdmin):

    list_display = ['from_country_as', 'data_gb_per_month', 'to_country']

    def from_country_as(self,obj):
        try:
            return obj.from_country.country.name
        except:
            return obj.from_country




admin.site.register(Country, CountryAdmin)
admin.site.register(PingData, PingDataAdmin)
admin.site.register(MasterData, MasterDataAdmin)
admin.site.register(InternetDataFlow, DataFlowAdmin)
admin.site.register(DataFlowMatrix, DataFlowMatrixAdmin)


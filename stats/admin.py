from django.contrib import admin
from .models import Statistics, Errors
from cinemas.models import Showtimes, Cinemas
from services.models import SeasonServices, MoviesServices
from .models import AppUsers
import datetime
from dateutil.relativedelta import relativedelta
import pytz
from django.db.models import Count, When, Case, Value, Q
import json

utc=pytz.UTC
# Register your models here.

class StatisticsChartsAdmin(admin.ModelAdmin):
    change_list_template = 'change_list.html'
    

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        today_date = datetime.datetime.today().date()
        
        last_day = datetime.datetime.today().astimezone() - datetime.timedelta(days=6)
        numdays = 7
        base = datetime.datetime.today().astimezone()

        count_showtimes_query = Showtimes.objects.filter(updated_at__gt = last_day).annotate(
            day = Case(
                When(updated_at__contains = today_date, then=Value('day1')),
                When(updated_at__contains = today_date - datetime.timedelta(days=1), then=Value('day2')),
                When(updated_at__contains = today_date - datetime.timedelta(days=2), then=Value('day3')),
                When(updated_at__contains = today_date - datetime.timedelta(days=3), then=Value('day4')),
                When(updated_at__contains = today_date - datetime.timedelta(days=4), then=Value('day5')),
                When(updated_at__contains = today_date - datetime.timedelta(days=5), then=Value('day6')),
                When(updated_at__contains = today_date - datetime.timedelta(days=6), then=Value('day7')),
            )
        ).aggregate(
            day1_count = Count('day',filter=Q(day='day1')),
            day2_count = Count('day',filter=Q(day='day2')),
            day3_count = Count('day',filter=Q(day='day3')),
            day4_count = Count('day',filter=Q(day='day4')),
            day5_count = Count('day',filter=Q(day='day5')),
            day6_count = Count('day',filter=Q(day='day6')),
            day7_count = Count('day',filter=Q(day='day7')),
        )
        count_showtimes_query = dict(reversed(list(count_showtimes_query.items())))

        # num_of_st = Showtimes.objects.filter(updated_at__gt = last_day).order_by("updated_at").values("id", "updated_at")
        date_list = [(base - datetime.timedelta(days=x)).strftime("%A, %d.%m") for x in range(numdays)][::-1]
        # st_dates = [(base - datetime.timedelta(days=x)).strftime("%d.%m.%Y") for x in range(numdays)]
        extra_context['date_list'] = date_list
        # extra_context['num_of_st'] = num_of_st

        # showtimes_count = {}

        # for st in num_of_st:
        #     if st["updated_at"].date().strftime("%d.%m.%Y") in showtimes_count.keys():
        #         showtimes_count[st["updated_at"].date().strftime("%d.%m.%Y")] += 1
        #     else: 
        #         showtimes_count[st["updated_at"].date().strftime("%d.%m.%Y")] = 1

        # showtimes_count = [showtimes_count[k] for k in showtimes_count.keys()]


        extra_context['count_showtimes_query'] = count_showtimes_query

        #-------------Netflix/Amazon Tvshows and movies ---------------#

        # Netflix id = 1
        # Amazon ids = 2, 18
        ids = [1, 2, 18]
        shows = SeasonServices.objects.filter(service__in = ids, updated_at__gte = last_day).values("updated_at", "service")
        movies = MoviesServices.objects.filter(service__in = ids, updated_at__gte = last_day).values("updated_at", "service")
        netflix_shows_count = {}
        amazon_shows_count = {}
        for st in shows:
            if st['service'] == 1:
                if st["updated_at"].date().strftime("%d.%m.%Y") in netflix_shows_count.keys():
                    netflix_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] += 1
                else: 
                    netflix_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] = 1
            else:
                if st["updated_at"].date().strftime("%d.%m.%Y") in amazon_shows_count.keys():
                    amazon_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] += 1
                else: 
                    amazon_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] = 1
        for st in movies:
            if st['service'] == 1:
                if st["updated_at"].date().strftime("%d.%m.%Y") in netflix_shows_count.keys():
                    netflix_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] += 1
                else: 
                    netflix_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] = 1
            else:
                if st["updated_at"].date().strftime("%d.%m.%Y") in amazon_shows_count.keys():
                    amazon_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] += 1
                else: 
                    amazon_shows_count[st["updated_at"].date().strftime("%d.%m.%Y")] = 1

        basic_date_list = [(base - datetime.timedelta(days=x)).strftime("%d.%m.%Y") for x in range(numdays)]

        for day in basic_date_list:
            if day not in netflix_shows_count:
                netflix_shows_count[day] = 0
            if day not in amazon_shows_count:
                amazon_shows_count[day] = 0
        
        netflix_shows_count = dict(sorted(netflix_shows_count.items(),key=lambda x:x[0],reverse=False))
        amazon_shows_count = dict(sorted(amazon_shows_count.items(),key=lambda x:x[0],reverse=False))
        
        extra_context['netflix_shows_count'] = netflix_shows_count
        extra_context['amazon_shows_count'] = amazon_shows_count


        #----------AppUsers-------------#

        quarters = {
            "first_quarter": [1, 2, 3],
            "second_quarter": [4, 5, 6],
            "third_quarter": [7, 8, 9],
            "fourth_quarter": [10, 11, 12],
            }
        today = datetime.datetime.today().astimezone()

        current_month = datetime.datetime.now().month

        for key, value in quarters.items():
            if current_month in value:
                current_quarter = key

        # filter_date = today - relativedelta(months=13)
        # all_app_users = AppUsers.objects.filter(updated_at__gte = filter_date).values()
        # all_app_users = AppUsers.objects.none()

        year = datetime.datetime.now().year

        # full_quarters = {
        #     "first_quarter" : [f'01.01.{year}', f'31.03.{year}'],
        #     "second_quarter" : [f'01.04.{year}', f'31.06.{year}'],
        #     "third_quarter" : [f'01.07.{year}', f'30.09.{year}'],
        #     "fourth_quarter" : [f'01.10.{year}', f'31.12.{year}']
        # }
        full_quarters = {
                "first_quarter" : [datetime.datetime(year,1,1).astimezone(), datetime.datetime(year,3,31).astimezone()],
                "second_quarter" : [datetime.datetime(year,4,1).astimezone(), datetime.datetime(year,6,30).astimezone()],
                "third_quarter" : [datetime.datetime(year,7,1).astimezone(), datetime.datetime(year,9,30).astimezone()],
                "fourth_quarter" : [datetime.datetime(year,10,1).astimezone(), datetime.datetime(year,12,31).astimezone()],
            }
        first_quarter = None
        second_quarter = None
        third_quarter = None
        fourth_quarter = None
        
        for _ in full_quarters:
            for key, value in full_quarters.items():
                if key == current_quarter:
                    if not first_quarter:
                        first_quarter = value
                        continue
                    if not second_quarter:
                        second_quarter = value
                        continue
                    if not third_quarter:
                        third_quarter = value
                        continue
                    if not fourth_quarter:
                        fourth_quarter = value
                        continue
            next_month_date = (today - relativedelta(months=3))
            next_month = next_month_date.month
            for key, value in quarters.items():
                if next_month in value:
                    current_quarter = key
            year_date = (today - relativedelta(months=3))
            year = year_date.year
    
            full_quarters = {
                "first_quarter" : [datetime.datetime(year,1,1).astimezone(), datetime.datetime(year,3,31).astimezone()],
                "second_quarter" : [datetime.datetime(year,4,1).astimezone(), datetime.datetime(year,6,30).astimezone()],
                "third_quarter" : [datetime.datetime(year,7,1).astimezone(), datetime.datetime(year,9,30).astimezone()],
                "fourth_quarter" : [datetime.datetime(year,10,1).astimezone(), datetime.datetime(year,12,31).astimezone()],
            }
            today = next_month_date

        # in final_aurters u can change the order of the quarters
        # first_quarter -> current quarter
        final_quarters = {
            "first_quarter" : fourth_quarter, 
            "second_quarter" : third_quarter, 
            "third_quarter" : second_quarter, 
            "fourth_quarter" : first_quarter # this is current  quarter
        }
       
        count_query = AppUsers.objects.filter(updated_at__gte = fourth_quarter[0]).aggregate(
            q1_count = Count('pk',filter=Q(updated_at__gte =first_quarter[0], created_at__lte =first_quarter[1])),
            q2_count = Count('pk',filter=Q(updated_at__gte =second_quarter[0], created_at__lte =second_quarter[1])),
            q3_count = Count('pk',filter=Q(updated_at__gte =third_quarter[0], created_at__lte =third_quarter[1])),
            q4_count = Count('pk',filter=Q(updated_at__gte =fourth_quarter[0], created_at__lte =fourth_quarter[1])),
        )
        count_query = dict(reversed(list(count_query.items())))

        # num_of_users_per_quarter = {

        #     quarter: len([user for user in all_app_users if (
                
        #          user["updated_at"]>=final_quarters[quarter][0] and user['created_at']<= final_quarters[quarter][1] )])
        #     for quarter in final_quarters
        # } 
        ## to remove tz from graf 

        extra_context['final_quarters'] = final_quarters
        extra_context['count_query'] = count_query

        #-------------------------------Active cinemas-----------------------#

        active_cinemas = Cinemas.objects.filter(active = 1).count()
        extra_context['today'] = today.strftime("%d.%m.%Y")
        extra_context['active_cinemas'] = active_cinemas

        #------------------Number of parser erros, alerts and warnings per day -----------#
        # today = dan kad je pokrenut bot
        # last_day is 6 days ago from today

        all_errors = Errors.objects.filter(created_at__gte = last_day)

        num_erros_alerts_warnings = {}
        num_erros_alerts_warnings['error'] = 0
        num_erros_alerts_warnings['alert'] = 0
        num_erros_alerts_warnings['warning'] = 0
        jsonDec = json.decoder.JSONDecoder()

        for obj in all_errors:
            if obj.error:
                num_erros_alerts_warnings['error'] += len(jsonDec.decode(obj.error))
            if obj.alert:
                num_erros_alerts_warnings['alert'] += len(jsonDec.decode(obj.alert))
            if obj.warning:
                num_erros_alerts_warnings['warning'] += len(jsonDec.decode(obj.warning))
        
        extra_context['num_erros_alerts_warnings'] = num_erros_alerts_warnings

        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = Statistics.objects.none()
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Statistics, StatisticsChartsAdmin)
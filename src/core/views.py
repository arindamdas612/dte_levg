import pandas as pd
import os
from datetime import datetime
import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.admin.views.decorators import staff_member_required

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import *
from .forms import AddFYDataForm, FileViewForm, CustomPasswordChangeForm
from .models import FyDataSummary, ReportLog


# Create your views here.


@login_required(login_url='/login/')
def home(request):
    form = FileViewForm()
    if request.method == 'POST':
        form = FileViewForm(request.POST)
        if form.is_valid():
            selected_file_id = form.cleaned_data['file_to_view']
            smry_data = FyDataSummary.objects.get(pk=selected_file_id)
            selected_file_name = smry_data.filename
            file_details = get_initial_filter_data(selected_file_name)
            context = {
                'page_title': 'Filter Data',
                'options': file_details,
                'filename': selected_file_name.split('.')[0],
            }
            return render(request, 'filters.html', context=context)
    context = {
        'page_title': 'Select PY Data',
        'form': form,
    }
    return render(request, 'home.html', context=context)


@login_required(login_url='/login/')
def process_filter(request, filename):
    if request.method == 'POST':
        data = request.POST
        portfolios = format_selctions(data.getlist('portfolio'))
        offerings = format_selctions(data.getlist('offering'))
        emp_portfolios = format_selctions(data.getlist('emp-portfolio'))
        emp_offerings = format_selctions(data.getlist('emp-offering'))
        clients = format_selctions(data.getlist('client'))
        projects = format_selctions(data.getlist('project'))

        df = get_filtered_data(filename, portfolios, offerings, emp_portfolios,
                               emp_offerings, clients, projects)
        processed_data = process_filltered_data(df)
        df_js = df
        df_js.columns = ['clientNumber', 'clientName', 'employeeNameCombined', 'employeeEmailAddress', 'employeeJobLevel', 'refinedJL', 'employeeAtPostingProfitCenter', 'employeeAtPostingProfitCenterDecp', 'employeeProfitCenterBusinessArea',
                         'employeeProfitCenterBusinessLine', 'profitCenterUSIIndicator', 'wbsLevel1', 'wbsLevel1Text', 'wbsLevel2', 'wbsLevel2Text', 'wbsBusinessModelMix', 'marketOfferingSolution', 'marketOfferingSubSolution', 'clientServiceHours', 'FTE']
        log = ReportLog(viewed_by=request.user)
        log.save()
    context = {
        'page_title': filename.split('_')[0],
        'result_list': processed_data['data'],
        'result_summary': processed_data['summary'],
        'supporting_data': df_js.to_dict('records'),
    }
    return render(request, 'show_data.html', context=context)


@login_required(login_url='/login/')
@staff_member_required
def fy_data(request):
    if request.method == 'POST':
        form = AddFYDataForm(request.POST, request.FILES)
        if form.is_valid():
            fy_data = zipped_file = request.FILES['data_file']

            dd_file = pd.read_excel(fy_data)
            if validate_data(dd_file):
                year = form.cleaned_data['year']
                period = form.cleaned_data['period']
                tot_records, _ = dd_file.shape
                total_fte = round(dd_file['FTE'].sum(), 2)
                fy_data = FyDataSummary.objects.filter(
                    year=year, period=period, no_of_records=tot_records, total_fte=total_fte).first()
                if fy_data:
                    messages.info(
                        request, f"The data already exists with file name {fy_data.filename}")
                else:
                    filename = f"FY{str(year)[2:]}P{period}_{datetime.now().strftime('%m%d%y_%H%M%S')}.csv"
                    dd_file.to_csv('CSV/' + filename)
                    s_data = FyDataSummary(
                        year=year,
                        period=period,
                        no_of_records=tot_records,
                        total_fte=total_fte,
                        filename=filename,
                        created_by=request.user,
                    )
                    s_data.save()
                    form = AddFYDataForm()
                    messages.success(
                        request, f"{filename} saved with {s_data.no_of_records} records and Total FTE is {round(s_data.total_fte,2)}")
            else:
                messages.error(
                    request, f"Invalid File Template")
    else:
        form = AddFYDataForm()
    fy_summary = FyDataSummary.objects.all().order_by('-create_ts')
    context = {
        'page_title': 'FY Data',
        'form': form,
        'summary_data': fy_summary,
    }
    return render(request, 'fy_data.html', context=context)


@login_required(login_url='/login/')
@staff_member_required
def del_fy_data(request, sumry_id):
    sumry = FyDataSummary.objects.get(id=sumry_id)
    print(f"CSV/{sumry.filename}")
    print(os.path.exists(f"CSV/{sumry.filename}"))
    if os.path.exists(f"CSV/{sumry.filename}") and not sumry.filename:
        os.remove(f"CSV/{sumry.filename}")
    sumry.delete()
    messages.success(request, f"FY Data deleted")
    return redirect('fy_data')


class FilterOptionsApiView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, format=None):
        data = request.POST

        filename = data['filename'] + '.csv'

        portfolio = data.getlist('portfolio[]')
        offering = data.getlist('offering[]')
        emp_portfolio = data.getlist('emp_portfolio[]')
        emp_offering = data.getlist('emp_offering[]')
        client = data.getlist('client[]')
        project = data.getlist('project[]')
        options = filter_data(filename, portfolio, offering, emp_portfolio,
                              emp_offering, client, project)
        return Response(options)


class ChartDataApiView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        file_details = get_file_stats()
        hit_data = get_view_data()
        return Response({
            'file_data': file_details,
            'view_data': hit_data[0],
            'hit_ratio': hit_data[1],
        })


class ChangePassword(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        form_class = CustomPasswordChangeForm
        form = form_class(self.request.user)
        return render(request, 'change_password.html', {'form': form, 'password_changed': False})

    def post(self, request, *args, **kwargs):
        form_class = CustomPasswordChangeForm
        form = form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return render(request, 'change_password.html', {'form': form, 'password_changed': True})
        else:
            return render(request, 'change_password.html', {'form': form, 'password_changed': False})

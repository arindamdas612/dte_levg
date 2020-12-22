import pandas as pd
import numpy as np
import json
from datetime import datetime, timezone as t1, timedelta
from dateutil.tz import *

from django.contrib.auth.models import User

from django.db.models.functions import TruncDay
from django.db.models import Count

from django.utils import timezone

from .models import FyDataSummary, ReportLog

COLUMNS_TO_CHECK = [
    'Client DUNS Number',
    'Client Name',
    'Employee Name Combined',
    'Employee Email Address',
    'Employee Job Level',
    'Refined JL',
    'Employee At Posting Profit Center',
    'Employee At Posting Profit Center Decp.',
    'Employee Profit Center Business Area',
    'Employee Profit Center Business Line',
    'Profit Center USI Indicator',
    'WBS Level 1',
    'WBS Level 1 Text',
    'WBS Level 2',
    'WBS Level 2 Text',
    'WBS Business Model Mix',
    'Market Offering Solution',
    'Market Offering Sub-Solution',
    'Client Service Hours',
    'FTE',
    160,
]

DESIG_CHECK = {
    'SM': [
        {'upper_limit': 0, 'lower_limit': -500,
            'color': '#7030a0', 'textColor': '#ffffff'},
        {'upper_limit': 0.7, 'lower_limit': 0,
            'color': '#ffff00', 'textColor': '#000000'},
        {'upper_limit': 1.1, 'lower_limit': 0.7,
            'color': '#92d050', 'textColor': '#000000'},
        {'upper_limit': 1.5, 'lower_limit': 1.1,
            'color': '#ffbf00', 'textColor': '#000000'},
        {'upper_limit': 500, 'lower_limit': 1.5,
            'color': '#ff0000', 'textColor': '#ffffff'},

    ],
    'M': [
        {'upper_limit': 3, 'lower_limit': -500,
            'color': '#7030a0', 'textColor': '#ffffff'},
        {'upper_limit': 5, 'lower_limit': 3,
            'color': '#ffff00', 'textColor': '#000000'},
        {'upper_limit': 8, 'lower_limit': 5,
            'color': '#92d050', 'textColor': '#000000'},
        {'upper_limit': 10, 'lower_limit': 8,
            'color': '#ffbf00', 'textColor': '#000000'},
        {'upper_limit': 500, 'lower_limit': 10,
            'color': '#ff0000', 'textColor': '#ffffff'},

    ],
    'SC': [
        {'upper_limit': 12, 'lower_limit': -500,
            'color': '#7030a0', 'textColor': '#ffffff'},
        {'upper_limit': 18, 'lower_limit': 12,
            'color': '#ffff00', 'textColor': '#000000'},
        {'upper_limit': 30, 'lower_limit': 18,
            'color': '#92d050', 'textColor': '#000000'},
        {'upper_limit': 36, 'lower_limit': 30,
            'color': '#ffbf00', 'textColor': '#000000'},
        {'upper_limit': 500, 'lower_limit': 36,
            'color': '#ff0000', 'textColor': '#ffffff'},

    ],
    'Con': [
        {'upper_limit': 20, 'lower_limit': -500,
            'color': '#7030a0', 'textColor': '#ffffff'},
        {'upper_limit': 31, 'lower_limit': 20,
            'color': '#ffff00', 'textColor': '#000000'},
        {'upper_limit': 51, 'lower_limit': 31,
            'color': '#92d050', 'textColor': '#000000'},
        {'upper_limit': 61, 'lower_limit': 51,
            'color': '#ffbf00', 'textColor': '#000000'},
        {'upper_limit': 500, 'lower_limit': 61,
            'color': '#ff0000', 'textColor': '#ffffff'},

    ],
    'Analyst':  [
        {'upper_limit': 12, 'lower_limit': -500,
            'color': '#7030a0', 'textColor': '#ffffff'},
        {'upper_limit': 18, 'lower_limit': 12,
            'color': '#ffff00', 'textColor': '#000000'},
        {'upper_limit': 30, 'lower_limit': 18,
            'color': '#92d050', 'textColor': '#000000'},
        {'upper_limit': 36, 'lower_limit': 30,
            'color': '#ffbf00', 'textColor': '#000000'},
        {'upper_limit': 500, 'lower_limit': 36,
            'color': '#ff0000', 'textColor': '#ffffff'},

    ],
    'AA':  [
        {'upper_limit': 1, 'lower_limit': -500,
            'color': '#7030a0', 'textColor': '#ffffff'},
        {'upper_limit': 3, 'lower_limit': 1,
            'color': '#ffff00', 'textColor': '#000000'},
        {'upper_limit': 5, 'lower_limit': 3,
            'color': '#92d050', 'textColor': '#000000'},
        {'upper_limit': 7, 'lower_limit': 5,
            'color': '#ffbf00', 'textColor': '#000000'},
        {'upper_limit': 500, 'lower_limit': 7,
            'color': '#ff0000', 'textColor': '#ffffff'},
    ],

}

FTE_CHECK = [
    {'upper_limit': 15, 'lower_limit': -100,
        'color': '#63faae', 'text_color': '#000000'},
    {'upper_limit': 75, 'lower_limit': 15,
        'color': '#bfe0f4', 'text_color': '#000000'},
    {'upper_limit': 250, 'lower_limit': 75,
        'color': '#608ffd', 'text_color': '#ffffff'},
    {'upper_limit': 500, 'lower_limit': 250,
        'color': '#77f1ff', 'text_color': '#000000'},
    {'upper_limit': 100000, 'lower_limit': 500,
        'color': '#c8c9ca', 'text_color': '#ffffff'},

]


def concatenate_p_c(p, c):
    c = 0 if c == np.nan else c
    p = 0 if p == np.nan else p
    st = ''
    try:
        st = f"{int(round(p, 0))}% ({round(c, 2)})"
    except Exception as e:
        st = f"0% ({c})"
    return '' if st == '0% (0.0)' or st == '0% (-0.00)' or st == '0% (0)' else st


def get_designation_color(p, pos, display_string):
    p = 0 if p == np.nan else round(p, 1)

    color = ''
    text_color = ''
    if display_string == '':
        color = ''
        text_color = ''
    else:
        try:
            for check in DESIG_CHECK[pos]:
                if p <= check['upper_limit'] and p > check['lower_limit']:
                    color = check['color']
                    text_color = check['textColor']
                    break
        except Exception as e:
            color = ''
            text_color = ''
    return [color, text_color]


def get_fte_color(fte_total):
    color = ''
    text_color = ''
    for check in FTE_CHECK:
        if fte_total <= check['upper_limit'] and fte_total > check['lower_limit']:
            color = check['color']
            text_color = check['text_color']
            break
    return [color, text_color]


def validate_data(data):
    invalid_columns = list(set(list(data.columns)) - set(COLUMNS_TO_CHECK))
    return False if len(invalid_columns) > 0 else True


def process_filltered_data(data):
    grouped_data = data.groupby(
        ['Client Name', 'WBS Level 1', 'WBS Level 1 Text', 'Refined JL'])['FTE'].sum().reset_index()
    dd_pivot = grouped_data.pivot_table(
        index=['Client Name', 'WBS Level 1', 'WBS Level 1 Text'], columns='Refined JL', aggfunc='sum', fill_value=0.0)
    flattened_dd = pd.DataFrame(dd_pivot.to_records())
    flattened_dd.columns = [hdr.replace("('FTE', ", "").replace(")", "").replace("'", "")
                            for hdr in flattened_dd.columns]

    flattened_dd_columns = list(flattened_dd.columns)

    if 'MD' not in flattened_dd_columns:
        flattened_dd['MD'] = 0.0
    if 'SM' not in flattened_dd_columns:
        flattened_dd['SM'] = 0.0
    if 'M' not in flattened_dd_columns:
        flattened_dd['M'] = 0.0
    if 'SC' not in flattened_dd_columns:
        flattened_dd['SC'] = 0.0
    if 'Con' not in flattened_dd_columns:
        flattened_dd['Con'] = 0.0
    if 'Analyst' not in flattened_dd_columns:
        flattened_dd['Analyst'] = 0.0
    if 'AA' not in flattened_dd_columns:
        flattened_dd['AA'] = 0.0

    flattened_dd = flattened_dd[['Client Name', 'WBS Level 1 Text',
                                 'WBS Level 1', 'MD', 'SM', 'M', 'SC', 'Con', 'Analyst', 'AA']]
    flattened_dd['Total FTE'] = flattened_dd['MD'] + flattened_dd['SM'] + flattened_dd['M'] + \
        flattened_dd['SC'] + flattened_dd['Con'] + \
        flattened_dd['Analyst'] + flattened_dd['AA']
    flattened_dd.columns = ['Client Name', 'Project Name',
                            'WBS Code', 'MD_C', 'SM_C', 'M_C', 'SC_C', 'Con_C', 'Analyst_C', 'AA_C', 'Total FTE_c']
    flattened_dd['MD_P'] = (flattened_dd['MD_C'] /
                            flattened_dd['Total FTE_c']) * 100
    flattened_dd['SM_P'] = (flattened_dd['SM_C'] /
                            flattened_dd['Total FTE_c']) * 100
    flattened_dd['M_P'] = (flattened_dd['M_C'] /
                           flattened_dd['Total FTE_c']) * 100
    flattened_dd['SC_P'] = (flattened_dd['SC_C'] /
                            flattened_dd['Total FTE_c']) * 100
    flattened_dd['Con_P'] = (
        flattened_dd['Con_C'] / flattened_dd['Total FTE_c']) * 100
    flattened_dd['Analyst_P'] = (
        flattened_dd['Analyst_C'] / flattened_dd['Total FTE_c']) * 100
    flattened_dd['AA_P'] = (flattened_dd['AA_C'] /
                            flattened_dd['Total FTE_c']) * 100
    # flattened_dd = flattened_dd[(flattened_dd['WBS Code'] == 'AAR00042-00')]
    # print(flattened_dd)
    # result = flattened_dd.round(decimals=1)
    t_fte = flattened_dd['Total FTE_c'].sum()
    md_c = flattened_dd['MD_C'].sum()
    md_p = (md_c/t_fte) * 100
    sm_c = flattened_dd['SM_C'].sum()
    sm_p = (sm_c/t_fte) * 100
    m_c = flattened_dd['M_C'].sum()
    m_p = (m_c/t_fte) * 100
    sc_c = flattened_dd['SC_C'].sum()
    sc_p = (sc_c/t_fte) * 100
    con_c = flattened_dd['Con_C'].sum()
    con_p = (con_c/t_fte) * 100
    a_c = flattened_dd['Analyst_C'].sum()
    a_p = (a_c/t_fte) * 100
    aa_c = flattened_dd['AA_C'].sum()
    aa_p = (aa_c/t_fte) * 100

    summary_dict = {
        'Total_FTE': t_fte,
        'MD': concatenate_p_c(md_p, md_c),
        'SM': concatenate_p_c(sm_p, sm_c),
        'M': concatenate_p_c(m_p, m_c),
        'SC': concatenate_p_c(sc_p, sc_c),
        'Con': concatenate_p_c(con_p, con_c),
        'Analyst': concatenate_p_c(a_p, a_c),
        'AA': concatenate_p_c(aa_p, aa_c),
        'MD_cl': get_designation_color(md_p, 'MD', concatenate_p_c(md_p, md_c))[0],
        'MD_tcl': get_designation_color(md_p, 'MD', concatenate_p_c(md_p, md_c))[1],
        'SM_cl': get_designation_color(sm_p, 'SM', concatenate_p_c(sm_p, sm_c))[0],
        'SM_tcl': get_designation_color(sm_p, 'SM', concatenate_p_c(sm_p, sm_c))[1],
        'M_cl': get_designation_color(m_p, 'M',  concatenate_p_c(m_p, m_c))[0],
        'M_tcl': get_designation_color(m_p, 'M',  concatenate_p_c(m_p, m_c))[1],
        'SC_cl': get_designation_color(sc_p, 'SC', concatenate_p_c(sc_p, sc_c))[0],
        'SC_tcl': get_designation_color(sc_p, 'SC', concatenate_p_c(sc_p, sc_c))[1],
        'Con_cl': get_designation_color(con_p, 'Con',  concatenate_p_c(con_p, con_c))[0],
        'Con_tcl': get_designation_color(con_p, 'Con',  concatenate_p_c(con_p, con_c))[1],
        'Analyst_cl': get_designation_color(a_p, 'Analyst', concatenate_p_c(a_p, a_c))[0],
        'Analyst_tcl': get_designation_color(a_p, 'Analyst', concatenate_p_c(a_p, a_c))[1],
        'AA_cl': get_designation_color(aa_p, 'AA', concatenate_p_c(aa_p, aa_c))[0],
        'AA_tcl': get_designation_color(aa_p, 'AA', concatenate_p_c(aa_p, aa_c))[1],
        'FTE_cl': get_fte_color(round(t_fte, 2))[0],
        'FTE_tcl': get_fte_color(round(t_fte, 2))[1],
    }
    result = flattened_dd
    res = result.to_dict('records')
    result_dict = [{
        'Client_Name': rec['Client Name'],
        'Project_Name': rec['Project Name'],
        'WBS_Code': rec['WBS Code'],
        'Total_FTE': round(rec['Total FTE_c'], 2),
        'MD': concatenate_p_c(rec['MD_P'], rec['MD_C']),
        'SM': concatenate_p_c(rec['SM_P'], rec['SM_C']),
        'M': concatenate_p_c(rec['M_P'], rec['M_C']),
        'SC':concatenate_p_c(rec['SC_P'], rec['SC_C']),
        'Con': concatenate_p_c(rec['Con_P'], rec['Con_C']),
        'Analyst': concatenate_p_c(rec['Analyst_P'], rec['Analyst_C']),
        'AA': concatenate_p_c(rec['AA_P'], rec['AA_C']),
        'MD_cl': get_designation_color(rec['MD_P'], 'MD', concatenate_p_c(rec['MD_P'], rec['MD_C']))[0],
        'MD_tcl': get_designation_color(rec['MD_P'], 'MD', concatenate_p_c(rec['MD_P'], rec['MD_C']))[1],
        'SM_cl': get_designation_color(rec['SM_P'], 'SM', concatenate_p_c(rec['SM_P'], rec['SM_C']))[0],
        'SM_tcl': get_designation_color(rec['SM_P'], 'SM', concatenate_p_c(rec['SM_P'], rec['SM_C']))[1],
        'M_cl': get_designation_color(rec['M_P'], 'M',  concatenate_p_c(rec['M_P'], rec['M_C']))[0],
        'M_tcl': get_designation_color(rec['M_P'], 'M',  concatenate_p_c(rec['M_P'], rec['M_C']))[1],
        'SC_cl': get_designation_color(rec['SC_P'], 'SC', concatenate_p_c(rec['SC_P'], rec['SC_C']))[0],
        'SC_tcl': get_designation_color(rec['SC_P'], 'SC', concatenate_p_c(rec['SC_P'], rec['SC_C']))[1],
        'Con_cl': get_designation_color(rec['Con_P'], 'Con', concatenate_p_c(rec['Con_P'], rec['Con_C']))[0],
        'Con_tcl': get_designation_color(rec['Con_P'], 'Con', concatenate_p_c(rec['Con_P'], rec['Con_C']))[1],
        'Analyst_cl': get_designation_color(rec['Analyst_P'], 'Analyst', concatenate_p_c(rec['Analyst_P'], rec['Analyst_C']))[0],
        'Analyst_tcl': get_designation_color(rec['Analyst_P'], 'Analyst', concatenate_p_c(rec['Analyst_P'], rec['Analyst_C']))[1],
        'AA_cl': get_designation_color(rec['AA_P'], 'AA', concatenate_p_c(rec['AA_P'], rec['AA_C']))[0],
        'AA_tcl': get_designation_color(rec['AA_P'], 'AA', concatenate_p_c(rec['AA_P'], rec['AA_C']))[1],
        'FTE_cl': get_fte_color(round(rec['Total FTE_c'], 2))[0],
        'FTE_tcl': get_fte_color(round(rec['Total FTE_c'], 2))[1],
    } for rec in res]

    response = {
        'data': result_dict,
        'code': 1 if len(result_dict) > 0 else 0,
        'summary': summary_dict
    }

    return response


def get_sorted_filter_columns(file_name):
    df = pd.read_csv(f"CSV/{file_name}")
    df = df[['Market Offering Solution', 'Market Offering Sub-Solution', 'Employee Profit Center Business Area',
             'Employee Profit Center Business Line', 'Client Name', 'WBS Level 1 Text', 'WBS Level 1']]
    df = df.drop_duplicates()
    df = df.sort_values(by=['Market Offering Solution', 'Market Offering Sub-Solution', 'Employee Profit Center Business Area',
                            'Employee Profit Center Business Line', 'Client Name', 'WBS Level 1 Text', 'WBS Level 1'])
    df = df.reset_index()
    df = df[['Market Offering Solution', 'Market Offering Sub-Solution', 'Employee Profit Center Business Area',
             'Employee Profit Center Business Line', 'Client Name', 'WBS Level 1 Text', 'WBS Level 1']]
    return df


def get_filter_text(df):
    portfolios = sorted(df['Market Offering Solution'].unique())
    offerings = sorted(df['Market Offering Sub-Solution'].unique())
    emp_portfolios = sorted(
        df['Employee Profit Center Business Area'].unique())
    emp_offerings = sorted(df['Employee Profit Center Business Line'].unique())
    client_names = sorted(df['Client Name'].unique())
    project_names = sorted(df['WBS Level 1 Text'].unique())

    filter_data = {
        'portfolio': ['All'] + portfolios if len(portfolios) > 1 else portfolios,
        'offering':  ['All'] + offerings if len(offerings) > 1 else offerings,
        'emp_portfolio':   ['All'] + emp_portfolios if len(emp_portfolios) > 1 else emp_portfolios,
        'emp_offering':   ['All'] + emp_offerings if len(emp_offerings) > 1 else emp_offerings,
        'client_name':   ['All'] + client_names if len(client_names) > 1 else client_names,
        'project_name':   ['All'] + project_names if len(project_names) > 1 else project_names,
    }
    return filter_data


def get_initial_filter_data(file_name):
    df = get_sorted_filter_columns(file_name)
    filter_data = get_filter_text(df)

    return json.dumps(filter_data)


def apply_filter(df, df_column, s_list):
    f_df = df
    if len(s_list) > 0:
        if s_list[0] != 'All' and s_list[0] != 'IG':
            f_df = df[df[df_column].isin(s_list)]

    return f_df


def filter_data(filename, portfolio, offering, emp_portfolio, emp_offering, client, project):
    df = get_sorted_filter_columns(filename)

    df = apply_filter(df, 'Market Offering Solution',  portfolio)
    df = apply_filter(df, 'Market Offering Sub-Solution',  offering)
    df = apply_filter(
        df, 'Employee Profit Center Business Area',  emp_portfolio)
    df = apply_filter(
        df, 'Employee Profit Center Business Line',  emp_offering)
    df = apply_filter(df, 'Client Name',  client)
    df = apply_filter(df, 'WBS Level 1 Text',  project)

    filter_data = get_filter_text(df)

    return json.dumps(filter_data)


def format_selctions(selection_list):
    p_list = ['All']
    if len(selection_list) > 0:
        if (selection_list[0] == 'All'):
            return p_list
        else:
            return selection_list
    else:
        return p_list


def get_filtered_data(filename, portfolio, offering, emp_portfolio, emp_offering, client, project):
    df = pd.read_csv(f"CSV/{filename}.csv")
    df = apply_filter(df, 'Market Offering Solution',  portfolio)
    df = apply_filter(df, 'Market Offering Sub-Solution',  offering)
    df = apply_filter(
        df, 'Employee Profit Center Business Area',  emp_portfolio)
    df = apply_filter(
        df, 'Employee Profit Center Business Line',  emp_offering)
    df = apply_filter(df, 'Client Name',  client)
    df = apply_filter(df, 'WBS Level 1 Text',  project)
    df = df[[
        'Client DUNS Number',
        'Client Name',
        'Employee Name Combined',
        'Employee Email Address',
        'Employee Job Level',
        'Refined JL',
        'Employee At Posting Profit Center',
        'Employee At Posting Profit Center Decp.',
        'Employee Profit Center Business Area',
        'Employee Profit Center Business Line',
        'Profit Center USI Indicator',
        'WBS Level 1',
        'WBS Level 1 Text',
        'WBS Level 2',
        'WBS Level 2 Text',
        'WBS Business Model Mix',
        'Market Offering Solution',
        'Market Offering Sub-Solution',
        'Client Service Hours',
        'FTE']]
    df = df.fillna('')
    return df


def get_user_counts():
    counts = [0, 0, 0]
    users = User.objects.all()
    for user in users:
        if user.is_superuser:
            counts[0] = counts[0] + 1
        elif user.is_staff:
            counts[1] = counts[1] + 1
        else:
            counts[2] = counts[2] + 1
    return counts


def get_file_stats():
    labels = []
    fte = []
    p_fte = []
    n_fte = []
    rec_count = []
    file_data = FyDataSummary.objects.all().order_by('year', 'period')
    for data in file_data:
        labels.append(data.display_filetag())
        fte.append(round(float(data.total_fte), 2))
        rec_count.append(data.no_of_records)

        d_file = pd.read_csv('CSV/' + data.filename)
        df_pfte = d_file[(d_file['FTE'] > 0)]
        df_nfte = d_file[(d_file['FTE'] <= 0)]

        p_fte.append(round(df_pfte['FTE'].sum(), 2))
        n_fte.append(round(df_nfte['FTE'].sum(), 2))

    return {
        'labels': labels,
        't_fte': fte,
        'p_fte': p_fte,
        'n_fte': n_fte,
        'count': rec_count,
    }


def get_application_start_date():
    activity_list = ReportLog.objects.values_list('view_ts')
    start_date = activity_list.order_by('view_ts').first()[0]
    start_date = timezone.localtime(start_date)
    return start_date


def current_date_with_tz():
    local = tzlocal()
    current_date = datetime.now()
    current_date = current_date.replace(tzinfo=local)
    return current_date


def get_total_run_days():
    return (current_date_with_tz() - get_application_start_date()).days


def date_exists(data, date_to_find):
    exists = False
    for d in data:
        if date_to_find in list(d.keys()):
            exists = True
            break
    return exists


def fill_missing_data(data, days):
    processe_data = {}
    for day in days:
        if date_exists(data, day):
            processe_data[day] = list(
                filter(lambda x: day in list(x.keys()), data))[0][day]
        else:
            processe_data[day] = 0
    return processe_data


def get_view_data():
    days = get_total_run_days()
    start_date = get_application_start_date()
    all_days = [(start_date + timedelta(days=d)).strftime("%Y-%m-%d")
                for d in range(1, days + 1)]
    hit_qs = ReportLog.objects.all().annotate(day=TruncDay(
        'view_ts')).values('day').annotate(c=Count('id')).order_by()
    hit_data = [{data['day'].strftime("%Y-%m-%d"): data['c']}
                for data in hit_qs]
    hit_data = fill_missing_data(hit_data, all_days)
    total_hit = sum(list(hit_data.values()))
    hit_ratio = round(total_hit / days, 2)

    return [hit_data, hit_ratio]

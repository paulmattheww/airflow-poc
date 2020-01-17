'''
https://medium.com/@dustinstansbury/understanding-apache-airflows-key-concepts-a96efed52b1a
'''
from datetime import datetime

# each Workflow/DAG must have a unique text identifier
WORKFLOW_DAG_ID = 'example_workflow_dag'

# start/end times are datetime objects
# here we start execution on Jan 1st, 2017
WORKFLOW_START_DATE = datetime(2017, 1, 1)

# schedule/retry intervals are timedelta objects
# here we execute the DAGs tasks every day
WORKFLOW_SCHEDULE_INTERVAL = timedelta(1)

# default arguments are applied by default to all tasks
# in the DAG
WORKFLOW_DEFAULT_ARGS = {
    'owner': 'example',
    'depends_on_past': False,
    'start_date': WORKFLOW_START_DATE,
    'email': ['example@example_company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

# initialize the DAG
dag = DAG(
    dag_id=WORKFLOW_DAG_ID,
    start_date=WORKFLOW_START_DATE,
    schedule_interval=WORKFLOW_SCHEDULE_INTERVAL,
    default_args=WORKFLOW_DEFAULT_ARGS,
)

########################
# Instantiating Tasks  #
########################

# instantiate the task to extract ad network revenue
extract_ad_revenue = ExtractAdRevenueOperator(
    task_id='extract_ad_revenue',
    dag=dag)

# dynamically instantiate tasks to extract app store data
APP_STORES = ['app_store_a', 'app_store_b', 'app_store_c']
app_store_tasks = []
for app_store in APP_STORES:
    task = ExtractAppStoreRevenueOperator(
        task_id='extract_{}_revenue'.format(app_store),
        dag=dag,
        app_store_name=app_store,
        )
    app_store_tasks.append(task)

# instantiate task to wait for conversion rates data avaibility
wait_for_conversion_rates = ConversionRatesSensor(
    task_id='wait_for_conversion_rates',
    dag=dag)

# instantiate task to extract conversion rates from API
extract_conversion_rates = ExtractConversionRatesOperator(
    task_id='get_conversion_rates',
    dag=dag)

# instantiate task to transform Spreadsheet data
transform_spreadsheet_data = TransformAdsSpreadsheetDataOperator(
    task_id='transform_spreadsheet_data',
    dag=dag)

# instantiate task transform JSON data from all app stores
transform_json_data = TransformAppStoreJSONDataOperator(
    task_id='transform_json_data',
    dag=dag,
    app_store_names=APP_STORES)

# instantiate task to apply currency exchange rates
perform_currency_conversions = CurrencyConversionsOperator(
    task_id='perform_currency_conversions',
    dag=dag)

# instantiate task to combine all data sources
combine_revenue_data = CombineDataRevenueDataOperator(
    task_id='combine_revenue_data',
    dag=dag)

# instantiate task to check that historical data exists
check_historical_data = CheckHistoricalDataOperator(
    task_id='check_historical_data',
    dag=dag)

# instantiate task to make predictions from historical data
predict_revenue = RevenuePredictionOperator(
    task_id='predict_revenue',
    dag=dag)


###############################
# Defining Tasks Dependencies #
###############################

# dependencies are set using the `.set_upstream` and/or
# `.set_downstream` methods
# (in version >=1.8.1, can also use the
# `extract_ad_revenue << transform_spreadsheet_data` syntax)

transform_spreadsheet_data.set_upstream(extract_ad_revenue)

# dynamically define app store dependencies
for task in app_store_tasks:
    transform_json_data.set_upstream(task)

extract_conversion_rates.set_upstream(wait_for_conversion_rates)

perform_currency_conversions.set_upstream(transform_json_data)
perform_currency_conversions.set_upstream(extract_conversion_rates)

combine_revenue_data.set_upstream(transform_spreadsheet_data)
combine_revenue_data.set_upstream(perform_currency_conversions)

check_historical_data.set_upstream(combine_revenue_data)

predict_revenue.set_upstream(check_historical_data)

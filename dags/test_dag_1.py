##################################################
# Examples of Custom Sensors / Operators (NoOps) #
##################################################

class ConversionRatesSensor(BaseSensorOperator):
    """
    An example of a custom Sensor. Custom Sensors generally overload
    the `poke` method inherited from `BaseSensorOperator`
    """
    def __init__(self, *args, **kwargs):
        super(ConversionRatesSensor, self).__init__(*args, **kwargs)

    def poke(self, context):
        print 'poking {}'.__str__()

        # poke functions should return a boolean
        return check_conversion_rates_api_for_valid_data(context)

class ExtractAppStoreRevenueOperator(BaseOperator):
    """
    An example of a custom Operator that takes non-default
    BaseOperator arguments.

    Extracts data for a particular app store identified by
    `app_store_name`.
    """
    def __init__(self, app_store_name, *args, **kwargs):
        self.app_store_name = app_store_name
        super(ExtractAppStoreRevenueOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        print 'executing {}'.__str__()

        # pull data from specific app store
        json_revenue_data = extract_app_store_data(self.app_store_name, context)

        # upload app store json data to filestore, can use context variable for
        # date-specific storage metadata
        upload_appstore_json_data(json_revenue_data, self.app_store_name, context)

class TransformAppStoreJSONDataOperator(BaseOperator):
    """
    An example of a custom Operator that takes non-default
    BaseOperator arguments.

    Extracts, transforms, and loads data for an array of app stores
    identified by `app_store_names`.
    """
    def __init__(self, app_store_names, *args, **kwargs):
        self.app_store_names = app_store_names
        super(TransformJSONDataOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        print 'executing {}'.__str__()

        # load all app store data from filestores. context variable can be used to retrieve
        # particular date-specific data artifacts
        all_app_stores_extracted_data = []
        for app_store in self.app_store_names:
            all_app_stores_extracted_data.append(extract_app_store_data(app_store, context))

        # combine all app store data, transform to proper format, and upload to filestore
        all_app_stores_json_data = combine_json_data(all_app_stores_extracted_data)
        app_stores_transformed_data = transform_json_data(all_app_stores_json_data)
        upload_data(app_stores_transformed_data, context)

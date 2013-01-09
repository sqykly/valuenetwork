from django.conf.urls import patterns, url


urlpatterns = patterns("",
    url(r"^projects/$", 'valuenetwork.valueaccounting.views.projects', name="projects"),
    url(r"^resources/$", 'valuenetwork.valueaccounting.views.resource_types', name="resource_types"),
    url(r"^contributions/(?P<project_id>\d+)/$", 'valuenetwork.valueaccounting.views.contributions', name="contributions"),
    url(r"^contributionhistory/(?P<agent_id>\d+)/$", 'valuenetwork.valueaccounting.views.contribution_history', name="contribution_history"),
    url(r"^logtime/$", 'valuenetwork.valueaccounting.views.log_time', name="log_time"),
    url(r"^value/(?P<project_id>\d+)/$", 'valuenetwork.valueaccounting.views.value_equation', name="value_equation"),
    url(r"^xbomfg/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.extended_bill', name="extended_bill"),
    url(r"^edit-xbomfg/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.edit_extended_bill', name="edit_extended_bill"),
    url(r"^network/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.network', name="network"),
    url(r"^timeline/$", 'valuenetwork.valueaccounting.views.timeline', name="timeline"),
    url(r"^jsontimeline/$", 'valuenetwork.valueaccounting.views.json_timeline', name="json_timeline"),
    url(r"^create-processtype-input/(?P<process_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.create_process_type_input', 
        name="create_process_type_input"),
    url(r"^create-processtype-feature/(?P<process_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.create_process_type_feature', 
        name="create_process_type_feature"),
    url(r"^change-feature/(?P<feature_id>\d+)/$", 'valuenetwork.valueaccounting.views.change_feature', 
        name="change_feature"),
    url(r"^delete-feature-confirmation/(?P<feature_id>\d+)/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.delete_feature_confirmation', 
        name="delete_feature_confirmation"),
    url(r"^delete-feature/(?P<feature_id>\d+)/$", 'valuenetwork.valueaccounting.views.delete_feature', 
        name="delete_feature"),
    url(r"^create-options-for-feature/(?P<feature_id>\d+)/$", 'valuenetwork.valueaccounting.views.create_options_for_feature', 
        name="create_options_for_feature"),
    url(r"^change-options-for-feature/(?P<feature_id>\d+)/$", 'valuenetwork.valueaccounting.views.change_options_for_feature', 
        name="change_options_for_feature"),
    url(r"^change-processtype-input/(?P<input_id>\d+)/$", 'valuenetwork.valueaccounting.views.change_process_type_input', 
        name="change_process_type_input"),
    url(r"^create-agent-resource-type/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.create_agent_resource_type', 
        name="create_agent_resource_type"),
    url(r"^change-agent-resource-type/(?P<agent_resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.change_agent_resource_type', 
        name="change_agent_resource_type"),
    url(r"^create-process-type-for-resource-type/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.create_process_type_for_resource_type', 
        name="create_process_type_for_resource_type"),
    url(r"^change-process-type/(?P<process_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.change_process_type', 
        name="change_process_type"),
    url(r"^change-resource-type/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.change_resource_type', 
        name="change_resource_type"),
    url(r"^create-resource-type/$", 'valuenetwork.valueaccounting.views.create_resource_type', 
        name="create_resource_type"),
    url(r"^delete-resource-type/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.delete_resource_type', 
        name="delete_resource_type"),
    url(r"^delete-resource-type-confirmation/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.delete_resource_type_confirmation', 
        name="delete_resource_type_confirmation"),
    url(r"^delete-process-type/(?P<process_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.delete_process_type', 
        name="delete_process_type"),
    url(r"^delete-process-type-confirmation/(?P<process_type_id>\d+)/(?P<resource_type_id>\d+)/$", 
        'valuenetwork.valueaccounting.views.delete_process_type_confirmation', 
        name="delete_process_type_confirmation"),
    url(r"^delete-process-input/(?P<process_input_id>\d+)/(?P<resource_type_id>\d+)/$", 
        'valuenetwork.valueaccounting.views.delete_process_input', 
        name="delete_process_input"),
    url(r"^delete-source/(?P<source_id>\d+)/(?P<resource_type_id>\d+)/$", 
        'valuenetwork.valueaccounting.views.delete_source', 
        name="delete_source"),
    url(r"^json-resourcetype-unit/(?P<resource_type_id>\d+)/$", 'valuenetwork.valueaccounting.views.json_resource_type_unit', 
        name="json_resource_type_unit"),
    url(r"^create-order/$", 'valuenetwork.valueaccounting.views.create_order', name="create_order"),
    url(r"^order-schedule/(?P<order_id>\d+)/$", 'valuenetwork.valueaccounting.views.order_schedule', name="order_schedule"),
    url(r"^delete-order/(?P<order_id>\d+)/$", 'valuenetwork.valueaccounting.views.delete_order', name="delete_order"),
    url(r"^delete-order-confirmation/(?P<order_id>\d+)/$", 'valuenetwork.valueaccounting.views.delete_order_confirmation', name="delete_order_confirmation"),
    url(r"^demand/$", 'valuenetwork.valueaccounting.views.demand', name="demand"),
    url(r"^supply/$", 'valuenetwork.valueaccounting.views.supply', name="supply"),
    url(r"^work/$", 'valuenetwork.valueaccounting.views.work', name="work"),
    url(r"^commit-to-task/(?P<commitment_id>\d+)/$", 'valuenetwork.valueaccounting.views.commit_to_task', 
        name="commit_to_task"),
    url(r"^work-commitment/(?P<commitment_id>\d+)/$", 'valuenetwork.valueaccounting.views.work_commitment', 
        name="work_commitment"),
    url(r"^process/(?P<process_id>\d+)/$", 'valuenetwork.valueaccounting.views.process_details', name="process_details"),
    url(r'^production-event/$', 'valuenetwork.valueaccounting.views.production_event_for_commitment', 
        name="production_event_for_commitment"),

)

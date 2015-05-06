import datetime

from django.db.models import Q
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import formset_factory, modelformset_factory, inlineformset_factory, BaseModelFormSet
from django.forms import ValidationError
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from valuenetwork.valueaccounting.models import *
from valuenetwork.equipment.forms import *
from valuenetwork.valueaccounting.views import get_agent


def consumable_formset(consumable_rt, data=None):
    ConsumableFormSet = formset_factory(form=ConsumableForm, extra=0)
    init = []
    consumable_resources = EconomicResource.objects.filter(resource_type=consumable_rt)
    for res in consumable_resources:
        d = {"resource_id": res.id,}
        init.append(d)   
    formset = ConsumableFormSet(initial=init, data=data)
    for form in formset:
        id = int(form["resource_id"].value())
        resource = EconomicResource.objects.get(id=id)
        form.identifier = resource.identifier
    return formset 

@login_required
def log_equipment_use(request, equip_resource_id, context_agent_id, pattern_id, equip_svc_rt_id, equip_fee_rt_id, tech_rt_id, consumable_rt_id, payment_rt_id, ve_id):
    #import pdb; pdb.set_trace()
    equipment = get_object_or_404(EconomicResource, id=equip_resource_id)
    equipment_svc_rt = get_object_or_404(EconomicResourceType, id=equip_svc_rt_id)
    equipment_fee_rt = get_object_or_404(EconomicResourceType, id=equip_fee_rt_id)
    technician_rt = EconomicResourceType.objects.get(id=tech_rt_id)
    context_agent = get_object_or_404(EconomicAgent, id=context_agent_id)
    pattern = ProcessPattern.objects.get(id=pattern_id)
    consumable_rt = EconomicResourceType.objects.get(id=consumable_rt_id)
    logged_on_agent = get_agent(request)
    ve = ValueEquation.objects.get(id=ve_id)
    init = {"event_date": datetime.date.today(), "from_agent": logged_on_agent}
    equip_form = EquipmentUseForm(equip_resource=equipment, context_agent=context_agent, initial=init, data=request.POST or None)
    formset = consumable_formset(consumable_rt=consumable_rt)
    
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if equip_form.is_valid():
            data = equip_form.cleaned_data
            input_date = data["event_date"]
            who = data["from_agent"]
            quantity = data["quantity"]
            technician = data["technician"]
            technician_quantity = data["technician_hours"]
            #process = data ["process"]
            et_ship = EventType.objects.get(name="Shipment")
            et_use = EventType.objects.get(name="Resource use")
            et_consume = EventType.objects.get(name="Resource Consumption")
            et_work = EventType.objects.get(name="Time Contribution")
            et_create = EventType.objects.get(name="Resource Production")
            et_fee = EventType.objects.get(name="Fee")
            total_price = 0

            process = Process(
                name="Paid service: Use of " + equipment.identifier,
                end_date=input_date,
                start_date=input_date,
                process_pattern=pattern,
                created_by=request.user,
                context_agent=context_agent,
                started=input_date,
                finished=True,
            )
            process.save()
            use_event = EconomicEvent(
                event_type = et_use,
                event_date = input_date,
                resource_type = equipment.resource_type,
                resource = equipment,
                process = process,
                from_agent = context_agent,
                to_agent = context_agent,
                context_agent = context_agent,
                quantity = quantity,
                unit_of_quantity = equipment.resource_type.unit_of_use,
                created_by = request.user,
            )
            use_event.save()
            formset = consumable_formset(data=request.POST, consumable_rt=consumable_rt)
            for form in formset.forms:
                if form.is_valid():
                    data_cons = form.cleaned_data
                    if data_cons:
                        qty = data_cons["quantity"]
                        if qty:
                            if qty > 0:
                                res_id = data_cons["resource_id"]
                                consumable = EconomicResource.objects.get(id=int(res_id))
                                price = consumable.compute_value_per_unit(value_equation=ve)
                                consume_event = EconomicEvent(
                                    event_type = et_consume,
                                    event_date = input_date,
                                    resource = consumable,
                                    resource_type = consumable.resource_type,
                                    process = process,
                                    from_agent = context_agent,
                                    to_agent = context_agent,
                                    context_agent = context_agent,
                                    quantity = qty,
                                    unit_of_quantity = consumable_rt.unit,
                                    value = price * qty,
                                    unit_of_value = consumable.resource_type.unit_of_price,
                                    created_by = request.user,
                                )
                                consume_event.save() 
                                total_price += consume_event.value    
            if technician and technician_quantity > 0:
                tech_event = EconomicEvent(
                    event_type = et_work,
                    event_date = input_date,
                    resource_type = technician_rt,
                    process = process,
                    from_agent = technician,
                    to_agent = context_agent,
                    context_agent = process.context_agent,
                    quantity = technician_quantity,
                    unit_of_quantity = technician_rt.unit,
                    value = quantity * technician_rt.price_per_unit,
                    unit_of_value = technician_rt.unit_of_price,
                    created_by = request.user,
                )
                tech_event.save()
                total_price += tech_event.value
            #ephemeral output resource
            printer_service = EconomicResource(
                resource_type=equipment_svc_rt,
                identifier="Temporary service resource 3D printing " + str(input_date) + " for " + who.nick,
                quantity=1,
                value_per_unit = total_price,
                created_by=request.user,
            )
            printer_service.save()
            output_event = EconomicEvent(
                event_type = et_create,
                event_date = input_date,
                resource_type = equipment_svc_rt,
                resource = printer_service,
                process = process,
                from_agent = context_agent,
                to_agent = context_agent,
                context_agent = process.context_agent,
                quantity = 1,
                unit_of_quantity = equipment_svc_rt.unit,
                value = total_price,
                unit_of_value = equipment_svc_rt.unit_of_price,
                created_by = request.user,
            )
            output_event.save()     
            #run distribution to get prices based on distributions
            #ve_exchange = Exchange(
            #    
            #)
            #dist = ve.run_value_equation_and_save(exchange=ve_exchange, money_resource=, amount_to_distribute, serialized_filters, cash_receipts=None, input_distributions=None):
            
            #import pdb; pdb.set_trace()
            owed = printer_service.compute_value_per_unit(value_equation=ve)
            sale = Exchange(
                name="Use of " + equipment.identifier,
                use_case=UseCase.objects.get(identifier="sale"),
                start_date=input_date,
                customer=who,
                context_agent=context_agent,
                created_by=request.user,
            )
            sale.save()
            #todo: hardcoded fee event
            mtnce_fee_event = EconomicEvent(
                event_type = et_fee,
                event_date = input_date,
                resource_type = equipment_fee_rt,
                exchange = sale,
                from_agent = who,
                to_agent = context_agent,
                context_agent = context_agent,
                quantity = use_event.quantity * equipment_fee_rt.price_per_unit,
                unit_of_quantity = equipment_fee_rt.unit_of_price,
                value = use_event.quantity * equipment_fee_rt.price_per_unit,
                unit_of_value = equipment_fee_rt.unit_of_price,
                created_by = request.user,
            )
            mtnce_fee_event.save()
            #owed += mtnce_fee_event.quantity
            ship_event = EconomicEvent(
                event_type = et_ship,
                event_date = input_date,
                resource_type = equipment_svc_rt,
                exchange = sale,
                from_agent = context_agent,
                to_agent = who,
                context_agent = context_agent,
                quantity = 1,
                unit_of_quantity = equipment_svc_rt.unit,
                value = owed,
                unit_of_value = equipment_svc_rt.unit_of_price,
                created_by = request.user,
            )
            ship_event.save()
            
            '''            
            if technician and technician_quantity > 0:
                tech_sale = Exchange(
                    name="Technician on " + equipment.identifier,
                    use_case=UseCase.objects.get(identifier="sale"),
                    start_date=input_date,
                    process_pattern=pattern,
                    customer=who,
                    created_by=request.user,
                    context_agent=context_agent,
                )
                tech_sale.save()
                tech_ship_event = EconomicEvent(
                    event_type = et_ship,
                    event_date = input_date,
                    resource_type = technician_rt,
                    exchange = tech_sale,
                    from_agent = technician,
                    to_agent = who,
                    context_agent = context_agent,
                    quantity = technician_quantity,
                    unit_of_quantity = technician_rt.unit,
                    value = technician_quantity * technician_rt.price_per_unit,
                    unit_of_value = technician_rt.unit_of_price,
                    created_by = request.user,
                )
                tech_ship_event.save()
            else:
                tech_sale = None
            #import pdb; pdb.set_trace()
            formset = consumable_formset(data=request.POST, consumable_rt=consumable_rt)
            for form in formset.forms:
                if form.is_valid():
                    data_cons = form.cleaned_data
                    if data_cons:
                        qty = data_cons["quantity"]
                        if qty:
                            if qty > 0:
                                res_id = data_cons["resource_id"]
                                consumable = EconomicResource.objects.get(id=int(res_id))
                                consume_ship_event = EconomicEvent(
                                    event_type = EventType.objects.get(name="Shipment"),
                                    event_date = input_date,
                                    resource = consumable,
                                    resource_type = consumable.resource_type,
                                    exchange = sale,
                                    from_agent = context_agent,
                                    to_agent = who,
                                    context_agent = context_agent,
                                    quantity = qty,
                                    unit_of_quantity = consumable_rt.unit,
                                    value = quantity * consumable.value_per_unit,
                                    unit_of_value = consumable.resource_type.unit_of_price,
                                    created_by = request.user,
                                )
                                consume_ship_event.save()
            '''                               
            return HttpResponseRedirect('/%s/%s/%s/%s/'
                % ('equipment/pay-equipment-use', sale.id, payment_rt_id, equip_resource_id))
    
    return render_to_response("equipment/log_equipment_use.html", {
        "equip_form": equip_form,
        "formset": formset,
        "equipment": equipment,
        "consumable_rt": consumable_rt,
    }, context_instance=RequestContext(request))

@login_required
def pay_equipment_use(request, sale_id, payment_rt_id, equip_resource_id):
    #import pdb; pdb.set_trace()
    sale = get_object_or_404(Exchange, id=sale_id)
    payment_rt = EconomicResourceType.objects.get(id=payment_rt_id)
    payment_unit = payment_rt.unit
    equipment = EconomicResource.objects.get(id=equip_resource_id)
    paid=False
    sale_total = Decimal(0)
    
    '''

    ship_events = sale.shipment_events()
    for se in ship_events:
        sale_total += se.value
    sale_total_formatted = "".join([payment_rt.unit.symbol, str(sale_total.quantize(Decimal('.01'), rounding=ROUND_UP))])
    if tech_sale_id:
        tech_events = tech_sale.shipment_events()
        for te in tech_events:
            tech_total += te.value
            technician = te.from_agent
        tech_total_formatted = "".join([payment_rt.unit.symbol, str(tech_total.quantize(Decimal('.01'), rounding=ROUND_UP))])    
    '''
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        
        
        '''        
            sale = Exchange(
                name="Use of " + equipment.identifier,
                use_case=UseCase.objects.get(identifier="sale"),
                start_date=input_date,
                customer=who,
                context_agent=context_agent,
                created_by=request.user,
            )
            sale.save()
            ship_event = EconomicEvent(
                event_type = et_ship,
                event_date = input_date,
                resource_type = equipment_svc_rt,
                exchange = sale,
                from_agent = context_agent,
                to_agent = who,
                context_agent = context_agent,
                quantity = 1,
                unit_of_quantity = equipment_svc_rt.unit,
                value = quantity * equipment__rt.price_per_unit,
                unit_of_value = equipment_use_rt.unit_of_price,
                created_by = request.user,
            )
            ship_event.save()
            if technician and technician_quantity > 0:
                tech_sale = Exchange(
                    name="Technician on " + equipment.identifier,
                    use_case=UseCase.objects.get(identifier="sale"),
                    start_date=input_date,
                    process_pattern=pattern,
                    customer=who,
                    created_by=request.user,
                    context_agent=context_agent,
                )
                tech_sale.save()
                tech_ship_event = EconomicEvent(
                    event_type = et_ship,
                    event_date = input_date,
                    resource_type = technician_rt,
                    exchange = tech_sale,
                    from_agent = technician,
                    to_agent = who,
                    context_agent = context_agent,
                    quantity = technician_quantity,
                    unit_of_quantity = technician_rt.unit,
                    value = technician_quantity * technician_rt.price_per_unit,
                    unit_of_value = technician_rt.unit_of_price,
                    created_by = request.user,
                )
                tech_ship_event.save()
            else:
                tech_sale = None
            #import pdb; pdb.set_trace()
            formset = consumable_formset(data=request.POST, consumable_rt=consumable_rt)
            for form in formset.forms:
                if form.is_valid():
                    data_cons = form.cleaned_data
                    if data_cons:
                        qty = data_cons["quantity"]
                        if qty:
                            if qty > 0:
                                res_id = data_cons["resource_id"]
                                consumable = EconomicResource.objects.get(id=int(res_id))
                                consume_ship_event = EconomicEvent(
                                    event_type = EventType.objects.get(name="Shipment"),
                                    event_date = input_date,
                                    resource = consumable,
                                    resource_type = consumable.resource_type,
                                    exchange = sale,
                                    from_agent = context_agent,
                                    to_agent = who,
                                    context_agent = context_agent,
                                    quantity = qty,
                                    unit_of_quantity = consumable_rt.unit,
                                    value = quantity * consumable.value_per_unit,
                                    unit_of_value = consumable.resource_type.unit_of_price,
                                    created_by = request.user,
                                )
                                consume_ship_event.save()



            mtnce_fee_event = EconomicEvent(
                event_type = et_use,
                event_date = input_date,
                resource_type = equipment_fee_rt,
                process = process,
                from_agent = context_agent,
                to_agent = context_agent,
                context_agent = context_agent,
                quantity = quantity,
                unit_of_quantity = equipment_fee_rt.unit,
                value = quantity * equipment_fee_rt.price_per_unit,
                unit_of_value = equipment_fee_rt.unit_of_price,
                created_by = request.user,
            )
            mtnce_fee_event.save()


                                

        '''            

        
        
        
        
        
        cr_et = EventType.objects.get(name="Cash Receipt")
        cr_event = EconomicEvent(
            event_type = cr_et,
            event_date = sale.start_date,
            exchange = sale,
            resource_type = payment_rt,
            from_agent = sale.customer,
            to_agent = sale.context_agent,
            context_agent = sale.context_agent,
            quantity = sale_total,
            unit_of_quantity = payment_unit,
            value = sale_total,
            unit_of_value = payment_unit,
            created_by = request.user,
        )
        cr_event.save()
        if tech_total > 0:
            tech_event = EconomicEvent(
                event_type = cr_et,
                event_date = tech_sale.start_date,
                exchange = tech_sale,
                resource_type = payment_rt,
                from_agent = tech_sale.customer,
                to_agent = technician,
                context_agent = sale.context_agent,
                quantity = tech_total,
                unit_of_quantity = payment_unit,
                value = tech_total,
                unit_of_value = payment_unit,
                created_by = request.user,
            )
            tech_event.save()
        paid = True
        
    return render_to_response("equipment/pay_equipment_use.html", {
        "process": process,
        "sale_total": sale_total_formatted,
        "payment_unit": payment_unit,
        "paid": paid,
        "equipment": equipment,
    }, context_instance=RequestContext(request))
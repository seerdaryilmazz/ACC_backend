import json
import re
import unicodedata
from datetime import date, timedelta, datetime
from enum import Enum

import requests

from accompany import todo_tasks
from accompany.utils import create_concurrent_request
from .model import Order, DelayedOrder, ProblematicOrder, ExpenseOrder


class OrderStateEnum(Enum):
    ACTIVE_ORDER = 650
    FINALIZED_ORDER = "100"
    PENDING_ORDER = "-1"
    PENDING_ORDER_MIN = "100"
    PENDING_ORDER_MAX = "420"
    ON_THE_ROAD_ORDER = "-2"
    ON_THE_ROAD_MAX_IMP = "500"
    ON_THE_ROAD_MAX_EXP = "580"
    CROSS_DOCK_ORDERS = "-3"
    CROSS_DOCK_MIN_EXP = "580"
    CROSS_DOCK_MAX_EXP = "614"
    CROSS_DOCK_MIN_IMP = "500"
    CROSS_DOCK_MAX_IMP = "595"
    ARCHIVED_ORDER = "650"
    CROSS_DOCK_LEAVING_ORDERS = "-4"
    CROSS_DOCK_LEAVING_ORDERS_MIN_IMP = "595"
    CROSS_DOCK_LEAVING_ORDERS_MAX_IMP = "650"
    CROSS_DOCK_LEAVING_ORDERS_MIN_EXP = "614"
    CROSS_DOCK_LEAVING_ORDERS_MAX_EXP = "650"


class TaskSubject(Enum):
    SPECIFIC_CUSTOMER_VISIT = 'SPECIFIC_CUSTOMER_VISIT'
    LANE_SPECIFIC_CUSTOMER_VISIT = 'LANE_SPECIFIC_CUSTOMER_VISIT'
    CUSTOMER_SPECIFIC_WORK = 'LANE_SPECIFIC_CUSTOMER_VISIT'
    CROSS_SELLING = 'CROSS_SELLING'
    SALES_LEAD_REDIRECTING = 'SALES_LEAD_REDIRECTING'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, TaskSubject))


class TaskStatus(Enum):
    OPEN = 'OPEN'
    COMPLETED = 'COMPLETED'
    CLOSED = 'CLOSED'
    CANCELED = 'CANCELED'
    POSTPONED = 'POSTPONED'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, TaskStatus))


class OrderStateHelper:
    @staticmethod
    def state_checker(order_state_value, order_state_enum, service_type):

        if order_state_enum is OrderStateEnum.ACTIVE_ORDER:
            return int(order_state_value) < int(OrderStateEnum.ACTIVE_ORDER.value)

        if order_state_enum is OrderStateEnum.FINALIZED_ORDER:
            return int(order_state_value) == int(OrderStateEnum.FINALIZED_ORDER.value)


        if order_state_enum is OrderStateEnum.PENDING_ORDER:
            return int(OrderStateEnum.PENDING_ORDER_MAX.value) > int(order_state_value) > int(OrderStateEnum.PENDING_ORDER_MIN.value)

        if order_state_enum is OrderStateEnum.ON_THE_ROAD_ORDER:
            if(service_type == "IMP"):
                return int(OrderStateEnum.ON_THE_ROAD_MAX_IMP.value) > int(order_state_value) >=int(OrderStateEnum.PENDING_ORDER_MAX.value)
            elif (service_type == "EXP"):
                return int(OrderStateEnum.ON_THE_ROAD_MAX_EXP.value) > int(order_state_value)  >=int(OrderStateEnum.PENDING_ORDER_MAX.value)

        if order_state_enum is OrderStateEnum.CROSS_DOCK_ORDERS:
            if (service_type == "IMP"):
                return int(OrderStateEnum.CROSS_DOCK_MAX_IMP.value) >= int(order_state_value) >= int(OrderStateEnum.CROSS_DOCK_MIN_IMP.value)
            elif (service_type == "EXP"):
                return int(OrderStateEnum.CROSS_DOCK_MAX_EXP.value) >= int(order_state_value) >= int(OrderStateEnum.CROSS_DOCK_MIN_EXP.value)

        if order_state_enum is OrderStateEnum.CROSS_DOCK_LEAVING_ORDERS:
            if (service_type == "IMP"):
                return int(OrderStateEnum.CROSS_DOCK_LEAVING_ORDERS_MAX_IMP.value) > int(order_state_value) > int(OrderStateEnum.CROSS_DOCK_LEAVING_ORDERS_MIN_IMP.value)
            elif (service_type == "EXP"):
                return int(OrderStateEnum.CROSS_DOCK_LEAVING_ORDERS_MAX_EXP.value) > int(order_state_value) > int(OrderStateEnum.CROSS_DOCK_LEAVING_ORDERS_MIN_EXP.value)




        if order_state_enum is OrderStateEnum.ARCHIVED_ORDER:
            return order_state_value == OrderStateEnum.ARCHIVED_ORDER.value


class QuadroBusiness:
    def __init__(self, quadro_api_url):
        self.quadro_api_url = quadro_api_url
        self.month_ago = date.today() - timedelta(days=60)

    def get_response_from_quadro(self, email, date_range,is_archive=False):
        self.month_ago = date.today() - timedelta(days=int(date_range))
        query_parameters = {'email': email, 'date': str(self.month_ago), 'isArchive': str(is_archive)}
        return requests.get(self.quadro_api_url, params=query_parameters)

    def get_archive_response_from_quadro(self, email,date_range,page_number,page_size):
        self.month_ago = date.today() - timedelta(days=int(date_range))
        query_parameters = {'email': email,'date': str(self.month_ago), 'isArchive': "true",'pageNumber':page_number,'pageSize':page_size}
        return requests.get(self.quadro_api_url, params=query_parameters)

    def get_specific_order_from_quadro(self, order_code, email):
        query_parameters = {'email': email, 'orderCode': order_code}
        r = requests.get(self.quadro_api_url, params=query_parameters).json()
        if len(r['Orders']) > 0:
            return json.loads(Order().make_order(r['Orders'][0], r['Delays'], r['Problems'], r['Expenses']))
        else:
            return {}

    def get_orders_from_quadro(self, is_archive, company_id, order_state, date_range, email, no_check_order_state=False,page_number=1,page_size = 1000000):
        if is_archive:
            response = self.get_archive_response_from_quadro(email,date_range=date_range,page_number=page_number,page_size = page_size)
        else:
            response = self.get_response_from_quadro(email, is_archive=is_archive,date_range=date_range)

        new_order_list = []
        order_list = response.json().get('Orders', [])
        delays = response.json()['Delays']
        problems = response.json()['Problems']
        expenses = response.json()['Expenses']
        i=0
        for x in order_list:
            try:
                if no_check_order_state or OrderStateHelper.state_checker(x['ORDER_STATE'], order_state, x['SERVICE_GROUP_CODE']):
                    temp_order = json.loads(Order().make_order(x,delays,problems,expenses))
                    
                    if i == 0:
                        temp_order['TotalCount'] = response.json()['TotalOrder'][0]['Count']
                        i=1

                    if company_id is not None:
                        if temp_order['CompanyId'] == company_id:
                            new_order_list.append(temp_order)
                    else:
                        new_order_list.append(temp_order)
            # Which means no key name 'ORDER_STATE'
            except KeyError:
                pass
        return new_order_list

    def get_orders_count_from_quadro(self, email,date_range):
        month_ago = date.today() - timedelta(days=date_range)
        user_email = email
        params = [{'email': user_email, 'date': str(month_ago), 'isArchive': str(False)},
                  {'email': user_email, 'date': str(month_ago),'isArchive': "true"}]
        response_list = create_concurrent_request(url_list=[self.quadro_api_url, self.quadro_api_url],
                                                  params_list=params)
        response_json = response_list[0]
        response_for_archive_json = response_list[1]

        active_order_count = 0
        finalized_order_count = 0
        to_the_road_order_count = 0
        on_the_road_order_count = 0
        on_the_terminal_order_count = 0
        archived_order_count = 0
        on_the_terminal_leaving_count = 0
        if response_json:
            for x in response_json.get('Orders', []):
                if OrderStateHelper.state_checker(x['ORDER_STATE'], OrderStateEnum.ACTIVE_ORDER,x['SERVICE_GROUP_CODE']):
                    active_order_count = active_order_count + 1
                if OrderStateHelper.state_checker(x['ORDER_STATE'], OrderStateEnum.FINALIZED_ORDER, x['SERVICE_GROUP_CODE']):
                    finalized_order_count = finalized_order_count + 1
                if OrderStateHelper.state_checker(x['ORDER_STATE'], OrderStateEnum.PENDING_ORDER,x['SERVICE_GROUP_CODE']):
                    to_the_road_order_count = to_the_road_order_count + 1
                if OrderStateHelper.state_checker(x['ORDER_STATE'], OrderStateEnum.ON_THE_ROAD_ORDER,x['SERVICE_GROUP_CODE']):
                    on_the_road_order_count = on_the_road_order_count + 1
                if OrderStateHelper.state_checker(x['ORDER_STATE'], OrderStateEnum.CROSS_DOCK_ORDERS,x['SERVICE_GROUP_CODE']):
                    on_the_terminal_order_count = on_the_terminal_order_count + 1
                if OrderStateHelper.state_checker(x['ORDER_STATE'], OrderStateEnum.CROSS_DOCK_LEAVING_ORDERS,x['SERVICE_GROUP_CODE']):
                    on_the_terminal_leaving_count = on_the_terminal_leaving_count + 1

        if response_for_archive_json:
            for y in response_for_archive_json.get('Orders', []):
                if OrderStateHelper.state_checker(y['ORDER_STATE'], OrderStateEnum.ARCHIVED_ORDER,y['SERVICE_GROUP_CODE']):
                    archived_order_count = archived_order_count + 1

        model = {
            "ActiveOrderCount": active_order_count,
            "FinalizedOrderCount": finalized_order_count,
            "ToTheRoadOrderCount": to_the_road_order_count,
            "OnTheRoadOrderCount": on_the_road_order_count,
            "OnTheTerminalOrderCount": on_the_terminal_order_count,
            "ArchivedOrderCount": archived_order_count,
            "OnTheTerminalLeavingCount":on_the_terminal_leaving_count
        }
        return model

    def  get_active_orders(self, email, is_archive, company_id,date_range):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=OrderStateEnum.ACTIVE_ORDER,date_range=date_range)

    def get_finalized_orders(self, email, is_archive, company_id,date_range):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=OrderStateEnum.FINALIZED_ORDER,date_range=date_range)

    def get_pending_orders(self, email, is_archive, company_id,date_range):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=OrderStateEnum.PENDING_ORDER,date_range=date_range)

    def get_on_the_road_orders(self, email, is_archive, company_id,date_range):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=OrderStateEnum.ON_THE_ROAD_ORDER,date_range=date_range)

    def get_cross_dock_orders(self, email, is_archive, company_id,date_range):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=OrderStateEnum.CROSS_DOCK_ORDERS,date_range=date_range)

    def get_cross_dock_leaving_orders(self, email, is_archive, company_id, date_range):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=OrderStateEnum.CROSS_DOCK_LEAVING_ORDERS, date_range=date_range)

    def get_archived_orders(self, email, is_archive, company_id,date_range,page_number=1,page_size=1000000):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=OrderStateEnum.ARCHIVED_ORDER,date_range=date_range,page_number=page_number,page_size=page_size)

    def get_all_orders(self, email, is_archive, company_id, order_state, no_check_order_state=True):
        return self.get_orders_from_quadro(email=email, is_archive=is_archive, company_id=company_id,
                                           order_state=order_state,
                                           no_check_order_state=no_check_order_state,date_range=10800)

    def get_new_location_orders(self, new_location_orders, username, email):
        new_location_orders_list = []
        documentList = list(new_location_orders.find({"$or": [{"CR_CODE": username}, {"SR_CODE": username}]},{'_id': False}))
        for x in documentList:
            order = self.get_specific_order_from_quadro(email=email, order_code=x['ORDER_CODE'])
            if order != {}:
                new_location_orders_list.append(order)
        return new_location_orders_list

    def get_all_task_type_count(self, is_archive, new_location_orders, complaints, email, todo_tasks, date_range=10800):
        response = self.get_response_from_quadro(email, is_archive=is_archive,date_range=date_range)
        new_location_order_count = len(self.get_new_location_orders(new_location_orders=new_location_orders, username=email.split('@')[0].upper(), email=email))

        userCondition = {"$or": [{"TaskOwner.email": email},
                                 {"TaskCreatedBy.email": email}]}
        model = {
            "DelayedOrderCount": len(
                DelayedOrder().make_delayed_order_list(response.json()['Orders'], response.json()['Delays'])),
            "ProblematicOrderCount": len(
                ProblematicOrder().make_problematic_order_list(response.json()['Problems'], response.json()['Orders'])),
            "ExpenseOrderCount": len(
                ExpenseOrder().make_expense_order_list(response.json()['Expenses'], response.json()['Orders'])),
            "NewLocationOrderCount": new_location_order_count,
            "ComplaintCount": complaints.find({"UserEmail": email,"ComplaintSolved":False}).count(),
            "TodosCount": todo_tasks.find({'$and': [userCondition, {"TaskStatus": {"$in": ['OPEN', 'POSTPONED']}}]}).count()

        }
        return model

    def get_delayed_orders(self, is_archive, email,date_range=10800):
        response = self.get_response_from_quadro(is_archive=is_archive, email=email,date_range=date_range)
        return DelayedOrder().make_delayed_order_list(response.json().get('Orders', []), response.json().get('Delays'))

    def get_problematic_orders(self, is_archive, email,date_range=10800):
        response = self.get_response_from_quadro(is_archive=is_archive, email=email,date_range=date_range)
        return ProblematicOrder().make_problematic_order_list(response.json().get('Problems', []),
                                                              response.json().get('Orders', []))

    def get_expense_orders(self, is_archive, email,date_range=10800):
        response = self.get_response_from_quadro(is_archive=is_archive, email=email,date_range=date_range)
        return ExpenseOrder().make_expense_order_list(response.json().get('Expenses', []),
                                                      response.json().get('Orders', []))

    def get_receivable_business(self, is_archive, company_id, email):
        response = self.get_response_from_quadro(is_archive=is_archive, email=email,date_range=10800)
        return list(filter(lambda x: x['COMPANY_CODE'] == company_id, response.json().get('ReceivableBusiness', [])))

    def get_prior_tasks(self, is_archive, email,date_range):
        response = self.get_response_from_quadro(is_archive=is_archive, email=email,date_range=date_range)

        delayed_order_list = DelayedOrder().make_delayed_order_list(response.json().get('Orders', []),
                                                                    response.json().get('Delays'))
        problematic_order_list = ProblematicOrder().make_problematic_order_list(response.json().get('Problems', []),
                                                                                response.json().get('Orders', []))
        expense_order_list = ExpenseOrder().make_expense_order_list(response.json().get('Expenses', []),
                                                                    response.json().get('Orders', []))
        prior_task_list = []
        delayed_order_list.sort(key=lambda x: datetime.strptime(x['DueDate'], "%Y-%m-%dT%H:%M:%S"))
        delayed_order_list = delayed_order_list[:10]
        problematic_order_list.sort(key=lambda x: datetime.strptime(x['ProblemDate'], "%Y-%m-%dT%H:%M:%S"))
        problematic_order_list = problematic_order_list[:10]
        expense_order_list.sort(key=lambda x: datetime.strptime(x['ExpenseDate'], "%Y-%m-%dT%H:%M:%S"))
        expense_order_list = expense_order_list[:10]

        for x in delayed_order_list:
            prior_task_list.append({'CustomerName': x['CustomerName'], 'OrderNo': x['OrderNo'], 'Date': x['DueDate'],
                                    'Type': 'DELAYED_ORDER', 'Model': x})

        for x in problematic_order_list:
            prior_task_list.append(
                {'CustomerName': x['CustomerName'], 'OrderNo': x['OrderNo'], 'Date': x['ProblemDate'],
                 'Type': 'PROBLEMATIC_ORDER', 'Model': x})

        for x in expense_order_list:
            prior_task_list.append(
                {'CustomerName': x['CustomerName'], 'OrderNo': x['OrderNo'], 'Date': x['ExpenseDate'],
                 'Type': 'EXPENSE_ORDER', 'Model': x})

        prior_task_list.sort(key=lambda x: datetime.strptime(x['Date'], "%Y-%m-%dT%H:%M:%S"))

        prior_task_list = prior_task_list[:10]
        return prior_task_list

    def set_unique_task_number(self, counter):
        counter_string = str(counter)
        return "T" + counter_string.zfill(6)
    
    def filter_todos(self, payload, user):
        startDate = payload.get("startDate")
        endDate = payload.get("endDate")
        query = payload.get("searchQuery")
        status = payload.get("status")
        subject = payload.get("subject")

        strippedQuery = unicodedata.normalize('NFD', query)
        strippedQuery = re.sub("[\u0300-\u036f]", "", strippedQuery)

        regexQuery = re.compile(query, re.IGNORECASE)
        strippedRegex = re.compile(strippedQuery, re.IGNORECASE)

        stringQuery = {"$or": []}
        stringQuery["$or"].append({"TaskCustomerAccount.AccountName": {"$in": [regexQuery]}})
        stringQuery["$or"].append({"TaskCustomerAccount.AccentsStrippedName": {"$in": [strippedRegex]}})
        stringQuery["$or"].append({"TaskStatus": {"$in": [regexQuery]}})
        stringQuery["$or"].append({"TaskNumber": {"$in": [regexQuery]}})
        stringQuery["$or"].append({"TaskCreatedBy.displayName": {"$in": [regexQuery]}})
        stringQuery["$or"].append({"TaskOwner.displayName": {"$in": [regexQuery]}})

        userCondition = {"$or": [{"TaskOwner.email": user},
                                 {"TaskCreatedBy.email": user}]}

        dateCondition = {'$and': []}
        if endDate is not None:
            dateCondition['$and'].append({"TaskDeadline": {"$lte": endDate}})
        if startDate is not None:
            dateCondition['$and'].append({"TaskDeadline": {"$gte": startDate}})

        finalQuery = {'$and': []}
        finalQuery['$and'].append(stringQuery)
        finalQuery['$and'].append(userCondition)
        if len(dateCondition['$and']) > 0:
            finalQuery['$and'].append(dateCondition)
        if status is not None and len(status) > 0:
            finalQuery['$and'].append({"TaskStatus": {"$in": status}})
        if subject is not None and len(subject) > 0:
            finalQuery['$and'].append({"TaskSubject": {"$in": subject}})

        todoList = todo_tasks.find(finalQuery)
        return list(todoList)


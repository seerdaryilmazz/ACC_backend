import json
from copy import deepcopy
from datetime import datetime, timedelta, date

from bson import ObjectId
from flask import request
from flask_jwt_extended import jwt_required
from flask_restplus import Resource
from pymongo import ReturnDocument

from accompany import logger, executor
from accompany import new_location_orders, selected_config, complaints, todo_tasks
from accompany.apis.quadro import api
from accompany.utils import Response, get_sequence, notify_user, send_text_email
from .business import QuadroBusiness, TaskSubject, TaskStatus
from .model import Order

server_response = Response()
quadro_business = QuadroBusiness(selected_config['QUADRO_API_URL'])

tr_task_subjects = {
    "SPECIFIC_CUSTOMER_VISIT": "Spesifik Müşteri Ziyareti",
    "LANE_SPECIFIC_CUSTOMER_VISIT": "Lane Spesifik Müşteri Ziyareti",
    "CUSTOMER_SPECIFIC_WORK": "Müşteri Spesifik Çalışması",
    "CROSS_SELLING": "Cross Selling",
    "SALES_LEAD_REDIRECTING": "Sales Lead Yönlendirilmesi"
}

@logger.register()
@api.route("/active_orders/<string:useremail>")
@api.route("/active_orders/<string:useremail>/<string:company_id>")
class ActiveOrders(Resource):
    #@jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail, company_id=None):
        date_range = request.args.get('dateRange')

        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_active_orders(is_archive=is_archive, company_id=company_id,email=useremail,date_range=date_range)

@logger.register()
@api.route("/finalized_orders/<string:useremail>")
@api.route("/finalized_orders/<string:useremail>/<string:company_id>")
class FinalizedOrders(Resource):
    @jwt_required
    @api.doc(description='Get finalized orders')
    def get(self, useremail, company_id=None):
        date_range = request.args.get('dateRange')
        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_finalized_orders(is_archive=is_archive, company_id=company_id,email=useremail,date_range=date_range)

@logger.register()
@api.route("/yola_cikacak_siparisler/<string:useremail>")
@api.route("/yola_cikacak_siparisler/<string:useremail>/<string:company_id>")
class PendingOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail, company_id=None):
        date_range = request.args.get('dateRange')

        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_pending_orders(is_archive=is_archive, company_id=company_id,email=useremail,date_range=date_range)

@logger.register()
@api.route("/yoldaki_siparisler/<string:useremail>")
@api.route("/yoldaki_siparisler/<string:useremail>/<string:company_id>")
class OnTheRoadOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail, company_id=None):
        date_range = request.args.get('dateRange')
        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_on_the_road_orders(is_archive=is_archive, company_id=company_id,email=useremail,date_range=date_range)

@logger.register()
@api.route("/terminaldeki_siparisler/<string:useremail>")
@api.route("/terminaldeki_siparisler/<string:useremail>/<string:company_id>")
class CrossDockOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail, company_id=None):
        date_range = request.args.get('dateRange')
        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_cross_dock_orders(is_archive=is_archive, company_id=company_id,email=useremail,date_range=date_range)

@logger.register()
@api.route("/terminalden_cikan_siparisler/<string:useremail>")
@api.route("/terminalden_cikan_siparisler/<string:useremail>/<string:company_id>")
class CrossDockOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail, company_id=None):
        date_range = request.args.get('dateRange')
        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_cross_dock_leaving_orders(is_archive=is_archive, company_id=company_id,email=useremail,date_range=date_range)

@logger.register()
@api.route("/archived_orders/<useremail>")
@api.route("/archived_orders/<useremail>/<string:company_id>")
class ArchivedOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail, company_id=None):
        date_range = request.args.get('dateRange')
        is_archive = request.args.get('isArchive', True)
        page_number = request.args.get('pageNumber',1)
        page_size = request.args.get('pageSize',1000000)
        return quadro_business.get_archived_orders(is_archive=is_archive, company_id=company_id,email=useremail,date_range=date_range,page_number=page_number,page_size=page_size)

@logger.register()
@api.route("/delayed_orders/<string:useremail>")
class DelayedOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail):
        is_archive = request.args.get('isArchive', False)
        date_range = request.args.get('dateRange',10800)
        return quadro_business.get_delayed_orders(is_archive=is_archive,email=useremail,date_range=date_range)

@logger.register()
@api.route("/get_new_location_orders/<string:user_name>/<string:email>")
class NewLocationOrders(Resource):
    #@jwt_required
    @api.doc(description='Get orders from new location')
    def get(self, user_name, email):
        return quadro_business.get_new_location_orders(new_location_orders=new_location_orders, username=user_name, email=email)

@logger.register()
@api.route("/problematic_orders/<string:useremail>")
class ProblematicOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail):
        is_archive = request.args.get('isArchive', False)
        date_range = request.args.get('dateRange',10800)
        return quadro_business.get_problematic_orders(is_archive=is_archive,email=useremail,date_range = date_range)

@logger.register()
@api.route("/expense_orders/<string:useremail>")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self, useremail):
        is_archive = request.args.get('isArchive', False)
        date_range = request.args.get('dateRange',10800)
        return quadro_business.get_expense_orders(is_archive=is_archive,email=useremail,date_range=date_range)

@logger.register()
@api.route("/notify_order_from_new_location")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def post(self):
        raw = api.payload
        created = new_location_orders.insert_one(raw).inserted_id
        if created:
            return server_response.success()
        return server_response.server_error()

@logger.register()
@api.route("/get_dashboard_task_and_order_counts_by_email/<string:email>/<int:date_range>")
class DashboardTaskAndOrderCounts(Resource):
    @jwt_required
    @api.doc(description='Get task and order counts by email')
    def get(self, email,date_range):

        order_count =quadro_business.get_orders_count_from_quadro(email,date_range=date_range)
        task_count = quadro_business.get_all_task_type_count(is_archive=False, new_location_orders=new_location_orders,
                                                             email=email, complaints=complaints, todo_tasks=todo_tasks, date_range=date_range)
        model = {
             "TaskSize": task_count["DelayedOrderCount"] + task_count["ProblematicOrderCount"] + task_count["ExpenseOrderCount"] +
                         task_count["NewLocationOrderCount"]  + task_count["ComplaintCount"]  + task_count["TodosCount"] ,
             "OrderSize": order_count['ActiveOrderCount']
         }
        return model

@logger.register()
@api.route("/get_all_task_type_count/<string:email>/<int:date_range>")
class AllTaskTypeCount(Resource):
    @jwt_required
    @api.doc(description='Get task and order counts by email')
    def get(self, email,date_range):
        return quadro_business.get_all_task_type_count(is_archive=False, new_location_orders=new_location_orders,
                                                       email=email, complaints=complaints, todo_tasks=todo_tasks, date_range=date_range)
@logger.register()
@api.route("/get_all_orders_type_count/<string:email>/<int:date_range>")
class AllOrdersTypeCount(Resource):
    #@jwt_required
    @api.doc(description='Get task and order counts by email')
    def get(self, email,date_range):
        return quadro_business.get_orders_count_from_quadro(email,date_range)

@logger.register()
@api.route("/get_all_orders/<string:useremail>")
@api.route("/get_all_orders/<string:useremail>/<string:company_id>")
class GetAllOrders(Resource):
    @jwt_required
    @api.doc(description='Get all orders')
    def get(self, useremail, company_id=None):
        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_all_orders(is_archive=is_archive, company_id=company_id, order_state=None,
                                              no_check_order_state=True,email=useremail)
@logger.register()
@api.route("/get_receivable_business/<string:useremail>")
@api.route("/get_receivable_business/<string:useremail>/<string:company_id>")
class GetReceivableBusiness(Resource):
    @jwt_required
    @api.doc(description='Get all orders')
    def get(self, useremail, company_id=None):
        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_receivable_business(is_archive=is_archive,company_id=company_id,email=useremail)

@logger.register()
@api.route("/get_prior_tasks/<string:useremail>/<int:date_range>")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self,useremail,date_range):
        is_archive = request.args.get('isArchive', False)
        return quadro_business.get_prior_tasks(is_archive=is_archive,email=useremail,date_range=date_range)

@logger.register()
@api.route("/get_specific_order/<string:orderCode>/<string:useremail>")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def get(self,useremail,orderCode):
        return quadro_business.get_specific_order_from_quadro(orderCode,useremail)


@logger.register()
@api.route("/save_complaint")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def post(self):
        raw = api.payload
        created = complaints.insert_one(raw).inserted_id
        try:
            if created:
                return server_response.success()
        except:
            return server_response.server_error("Sunucuda bir hata oluştu")

@logger.register()
@api.route("/edit_complaint")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Get active orders')
    def post(self):
        raw = api.payload
        edited = complaints.find_one_and_update({'_id': ObjectId(raw['_id']['$oid'])}, {'$set': {

            "ComplaintSubject": raw["ComplaintSubject"],
            "ComplaintCustomerAccountName": raw["ComplaintCustomerAccountName"],
            "ComplaintCustomerAccountId": raw["ComplaintCustomerAccountId"],
            "ComplaintCustomerAccountCompanyId": raw["ComplaintCustomerAccountCompanyId"],
            "ComplaintType": raw["ComplaintType"],
            "ComplaintDescription": raw["ComplaintDescription"],
            "ComplaintDueDate": raw["ComplaintDueDate"],
            "ComplaintSolved": raw["ComplaintSolved"],
            "ComplaintSolvedDescription": raw["ComplaintSolvedDescription"]

        }})
        try:
            if edited:
                return server_response.success()
        except:
            return server_response.server_error("Sunucuda bir hata oluştu")

@logger.register()
@api.route("/get_complaints/<string:email>")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Get user complaints')
    def get(self, email):
        return  list(complaints.find({"UserEmail": email,"ComplaintSolved":False}))


@logger.register()
@api.route("/get_task_subjects")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Get task subjects')
    def get(self):
        return TaskSubject.list()


@logger.register()
@api.route("/get_task_statuses")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Get task statuses')
    def get(self):
        return TaskStatus.list()


@logger.register()
@api.route("/save_todo_task")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Save to do task')
    def post(self):
        raw = api.payload
        notification = raw.get('notification')
        task = raw.get('task')
        for owner in task['TaskOwners']:
            newTask = deepcopy(task)
            del newTask['TaskOwners']
            newTask['TaskOwner'] = owner
            taskNumber = quadro_business.set_unique_task_number(get_sequence("task_counter"))
            newTask['TaskNumber'] = taskNumber
            try:
                todo_tasks.insert_one(newTask)
                notification['Content'] = notification['Content'].replace('TASK_NUMBER', taskNumber)
                notification['Url'] = 'pages/task/todo/' + taskNumber
                executor.submit(notify_user, data=notification, recipients=[owner['email']])
                executor.submit(send_text_email, body=notification['Content'], recipients=[owner['email']])
            except Exception as exception:
                return server_response.server_error("Sunucuda bir hata oluştu",
                                                    result_message="Exception: " + exception.__str__())

        return server_response.success()


@logger.register()
@api.route("/edit_todo_task")
class ExpenseOrders(Resource):
    @jwt_required
    @api.doc(description='Edit to do')
    def post(self):
        raw = api.payload
        notification = raw.get('notification')
        updatedTask = raw.get('updatedTask')
        updateDict = {}
        if updatedTask['TaskDescriptions'] is not None:
            updateDict['TaskDescriptions'] = updatedTask['TaskDescriptions']
        if updatedTask['TaskStatus'] is not None:
            updateDict['TaskStatus'] = updatedTask['TaskStatus']
        if updatedTask['TaskDeadline'] is not None:
            updateDict['TaskDeadline'] = updatedTask['TaskDeadline']

        try:
            edited = todo_tasks.find_one_and_update({'_id': ObjectId(updatedTask['_id']['$oid'])},
                                                {'$set': updateDict}, return_document=ReturnDocument.AFTER)
            if notification is not None:
                executor.submit(notify_user, data=notification, recipients=notification['User'])
                executor.submit(send_text_email, body=notification['Content'], recipients=notification['User'])
            return edited
        except Exception as exception:
            raise exception


@logger.register()
@api.route("/get_todo_task_by_taskNumber/<string:number>")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Get to do task list')
    def get(self, number):
        return todo_tasks.find_one({"TaskNumber": number}) or {}


@logger.register()
@api.route("/get_todo_tasks")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Get to do task list')
    def post(self):
        return quadro_business.filter_todos(api.payload, request.headers['X-On-Behalf-Of'])


@logger.register()
@api.route("/schedule_task_deadline")
class ExpenseOrders(Resource):
    # @jwt_required
    @api.doc(description='Get to do task list')
    def get(self):
        today = date.today()
        days_to_add = 5
        daylimit = today
        while days_to_add > 0:
            daylimit = daylimit + timedelta(days=1)
            if daylimit.weekday() >= 5:
                continue
            days_to_add -= 1
        tasks = list(todo_tasks.find(
            {"TaskDeadline": {"$lte": daylimit.isoformat(), "$gte": today.isoformat()}, "TaskStatus": {"$in": ["OPEN", "POSTPONED"]}}))
        for task in tasks:
            deadline = task['TaskDeadline'].replace("Z", "")
            customerContent = task.get("TaskCustomerAccount", {}).get("AccountName") + " müşterisi için " if task.get(
                "TaskCustomerAccount", {}).get("AccountName") else ""
            subjectContent = tr_task_subjects[task['TaskSubject']] + " tipli "
            numberContent = task['TaskNumber'] + " numaralı "
            deadlineContent = "Deadline: " + datetime.strftime(datetime.fromisoformat(deadline), "%d.%m.%Y") + " "

            content = ""
            if datetime.fromisoformat(deadline).day == today.day:
                content = customerContent + subjectContent + numberContent + "taskın deadline'ı bugün. Lütfen aksiyon alınız."
            else:
                content = customerContent + subjectContent + numberContent + "taskın deadline'ı yaklaştı. " + deadlineContent + "Bilginize."

            notification = {
                'Content': content,
                'CreatedAt': datetime.now().isoformat(),
                'Url': "pages/task/todo/" + task['TaskNumber']
            }
            executor.submit(notify_user, data=notification, recipients=[task['TaskOwner']['email']])
            executor.submit(send_text_email, body=content, recipients=[task['TaskOwner']['email']])
        return tasks


import json
from datetime import datetime as dt


class Order:
    @staticmethod
    def findImportOrExport(self,service_group_code, loading_company_info,delivery_company_info):
        country_code = loading_company_info.split('-')[0].rstrip()

        if (service_group_code == "IMP"):
            country_code = loading_company_info.split('-')[0].rstrip()
            return "İthalat<br> (" + country_code + ")"

        else:
            country_code = delivery_company_info.split('-')[0].rstrip()
            return "İhracat<br> (" + country_code + ")"

    def __init__(self, OrderNo="", CustomerName="", Service="", ReadyDate="", DeliveryDate="", Sender="",
                 LoadingPlace="", LoadingCompany="", ServiceType="",
                 DeliveryCompany="", DeliveryInformation="", Receiver="", CompanyId="", LDM="", PW = "", PackagingType="", GrossWeight="",Volume="",
                 EstimatedArrivalTime="",DueDate="", FullTruck="", OrderType="", ServiceGroup=""):
        self.OrderNo = OrderNo
        self.CustomerName = CustomerName
        self.Service = Service
        self.ReadyDate = ReadyDate
        self.DeliveryDate = DeliveryDate
        self.Sender = Sender
        self.LoadingInformation = LoadingPlace
        self.LoadingCompany = LoadingCompany
        self.ServiceType = ServiceType
        self.DeliveryCompany = DeliveryCompany
        self.DeliveryInformation = DeliveryInformation
        self.Receiver = Receiver
        self.CompanyId = CompanyId
        self.LDM = LDM
        self.PW = PW
        self.PackagingType = PackagingType
        self.GrossWeight = GrossWeight
        self.Volume =Volume
        self.EstimatedArrivalTime = EstimatedArrivalTime
        self.DueDate = DueDate
        self.FullTruck = FullTruck
        self.OrderType = OrderType
        self.ServiceGroup = ServiceGroup

    def make_order(self, json_object, delays, problems, expenses):
        self.OrderNo = json_object['ORDER_CODE']
        self.CustomerName = json_object['CUSTOMER_SHORT_NAME']
        self.ReadyDate = json_object['DATE_READY']
        self.DeliveryDate = json_object["DATE_OG"]
        self.Sender = json_object["SENDER_COMPANY_NAME"]
        self.LoadingCompany = json_object["LOADING_COMPANY_NAME"]
        self.LoadingInformation = json_object["LOADING_COMPANY_INFO"]
        self.ServiceType = json_object["SERVICE_TYPE_CODE"]
        self.DeliveryCompany = json_object["DELIVERY_CUSTOMER_COMPANY_NAME"]
        self.DeliveryInformation = json_object["DELIVERY_COMPANY_INFO"]
        self.Receiver = json_object["CONSIGNEE_COMPANY_NAME"]
        self.LDM = json_object["LDM"]
        self.PW = json_object["PW"]
        self.PackagingType = json_object["PACKAGING_TYPE"]
        self.GrossWeight = json_object["GROSS_WEIGHT"]
        self.Volume = json_object["VOLUME"]
        self.EstimatedArrivalTime = json_object["DATE_ETA"]
        self.DueDate = json_object["DATE_OG"]
        self.FullTruck = json_object['FULL_TRUCK']
        self.OrderType = json_object['ORDER_TYPE']
        self.ServiceGroup = json_object['SERVICE_GROUP_CODE']
        self.Service = Order.findImportOrExport(self,service_group_code=json_object['SERVICE_GROUP_CODE'], loading_company_info=json_object["LOADING_COMPANY_INFO"],delivery_company_info=json_object["DELIVERY_COMPANY_INFO"])

        self.Delay = self.make_delayed_order_for_order(delays,json_object)
        self.Problem = self.make_problematic_order_for_orders(problems,json_object)
        self.Expense = self.make_expense_order_for_order(expenses,json_object)
        self.CompanyId = json_object["CUSTOMER_COMPANY_CODE"]

        return self.toJSON()

    def make_specific_order(self, json_object):
        self.OrderNo = json_object['ORDER_CODE']
        self.CustomerName = json_object['CUSTOMER_SHORT_NAME']
        self.ReadyDate = json_object['DATE_READY']
        self.DeliveryDate = json_object["DATE_OG"]
        self.Sender = json_object["SENDER_COMPANY_NAME"]
        self.LoadingCompany = json_object["LOADING_COMPANY_NAME"]
        self.LoadingInformation = json_object["LOADING_COMPANY_INFO"]
        self.ServiceType = json_object["SERVICE_TYPE_CODE"]
        self.DeliveryCompany = json_object["DELIVERY_CUSTOMER_COMPANY_NAME"]
        self.DeliveryInformation = json_object["DELIVERY_COMPANY_INFO"]
        self.Receiver = json_object["CONSIGNEE_COMPANY_NAME"]
        self.CompanyId = json_object["CUSTOMER_COMPANY_CODE"]
        self.LDM = json_object["LDM"]
        self.PW = json_object["PW"]
        self.PackagingType = json_object["PACKAGING_TYPE"]
        self.GrossWeight = json_object["GROSS_WEIGHT"]
        self.Volume = json_object["VOLUME"]
        self.EstimatedArrivalTime = json_object["DATE_ETA"]
        self.DueDate = json_object["DATE_OG"]
        self.Service = Order.findImportOrExport(self,service_group_code=json_object['SERVICE_GROUP_CODE'],loading_company_info=json_object["LOADING_COMPANY_INFO"],delivery_company_info=json_object["DELIVERY_COMPANY_INFO"])

        self.Order = json_object

        return self.toJSON()

    def make_specific_order_for_new_location_orders(self, json_object):
        self.OrderNo = json_object['ORDER_CODE']
        self.CustomerName = json_object['CUSTOMER_COMPANY_NAME']
        #self.ReadyDate = json_object['DATE_READY']
        #self.DeliveryDate = json_object["DATE_OG"]
        self.Sender = json_object["SENDER_COMPANY_NAME"]
        self.LoadingCompany = json_object["LOADING_COMPANY_NAME"]
        self.LoadingInformation = json_object["LOADING_COMPANY_INFO"]
        #self.ServiceType = json_object["SERVICE_TYPE_CODE"]
        self.DeliveryCompany = json_object["DELIVERY_CUSTOMER_COMPANY_NAME"]
        self.DeliveryInformation = json_object["DELIVERY_COMPANY_INFO"]
        self.Receiver = json_object["CONSIGNEE_COMPANY_NAME"]
        self.CompanyId = json_object["CUSTOMER_COMPANY_CODE"]
        #self.LDM = json_object["LDM"]
        #self.PW = json_object["PW"]
        #self.PackagingType = json_object["PACKAGING_TYPE"]
        self.GrossWeight = json_object["GROSS_WEIGHT"]
        #self.Volume = json_object["VOLUME"]
        #self.EstimatedArrivalTime = json_object["DATE_ETA"]
        #self.DueDate = json_object["DATE_OG"]
        self.Service = Order.findImportOrExport(self,service_group_code=json_object['SERVICE_GROUP_CODE'],loading_company_info=json_object["LOADING_COMPANY_INFO"],delivery_company_info=json_object["DELIVERY_COMPANY_INFO"])

        self.Order = json_object

        return self.toJSON()     

    def make_problematic_order_for_orders(self, problems, order):
        for x in problems:
            if x['ORDER_CODE'] == order['ORDER_CODE']:
                self.OrderNo = x['ORDER_CODE']
                self.ProblemResource = x['RESOURCE_TYPE']
                self.ProblemType = x['PROBLEM_TYPE_DESC']
                self.ProblemDate = x['DATE_PROBLEM']
                self.ProblemNote = x['NOTE']
                self.ProblemDetail = x['PROBLEM_DETAIL']
                self.ProblemStatus = x['DURUMU']
                return json.loads(self.toJSON())

    def make_expense_order_for_order(self, expenses, order):
        for x in expenses:
            if x['ORDER_CODE'] == order['ORDER_CODE']:
                self.OrderNo = x['ORDER_CODE']
                self.ExpensePrice = str(x['PRICE']) + " " + x['CURRENCY']
                self.ExpenseReason = x['SERVICE_NAME']
                self.ExpenseDate = x['EXPENSE_DATE']
                self.ExpenseDescription = x['MAIL_NOTE']
                self.ExpenseCompany = x['EXPENSE_COMPANY']
                self.ExpenseResponsible = x['RESPONSIBLE']
                self.ExpenseStatus = x['STATUS']
                return json.loads(self.toJSON())

    def make_delayed_order_for_order(self, delays, order):
        for delay in delays:
            if delay['ORDER_CODE'] == order['ORDER_CODE']:
                estimated_arrival_time = dt.strptime(order['DATE_ETA'], "%Y-%m-%dT%H:%M:%S")
                due_date = dt.strptime(order['DATE_OG'], "%Y-%m-%dT%H:%M:%S")
                if estimated_arrival_time.date() > due_date.date():
                    self.DelayType = delay['REASON']
                    self.DelayResponsibility = delay['RESPONSIBILITY']
                    self.DelayDescription = delay['NOTE']
                    self.OrderNo = order['ORDER_CODE']
                    self.CustomerName = order['CUSTOMER_SHORT_NAME']
                    self.ReadyDate = order['DATE_READY']
                    self.EstimatedArrivalTime = order['DATE_ETA']
                    self.DueDate = order['DATE_OG']
                    self.Service = Order.findImportOrExport(self, service_group_code=order['SERVICE_GROUP_CODE'],
                                                            loading_company_info=order["LOADING_COMPANY_INFO"],delivery_company_info=order["DELIVERY_COMPANY_INFO"])

                    return json.loads(self.toJSON())

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class ProblematicOrder:
    def __init__(self, OrderNo="", CustomerName="", ProblemResource="", ProblemType="", ProblemDate="", ProblemNote="",
                 ProblemDetail="", ProblemStatus=""):
        self.OrderNo = OrderNo
        self.CustomerName = CustomerName
        self.ProblemResource = ProblemResource
        self.ProblemType = ProblemType
        self.ProblemDate = ProblemDate
        self.ProblemNote = ProblemNote
        self.ProblemDetail = ProblemDetail
        self.ProblemStatus = ProblemStatus

    def make_problematic_order_list(self, problems, orders):
        problematic_order_list = []
        for x in problems:
            if x['DATE_RESOLVE'] == None:
                self.OrderNo = x['ORDER_CODE']
                self.ProblemResource = x['RESOURCE_TYPE']
                self.ProblemType = x['PROBLEM_TYPE_DESC']
                self.ProblemDate = x['DATE_PROBLEM']
                self.ProblemNote = x['NOTE']
                self.ProblemDetail = x['PROBLEM_DETAIL']
                self.ProblemStatus = x['DURUMU']
                self.CustomerName = next((x for x in orders if x['ORDER_CODE'] == self.OrderNo), None)['CUSTOMER_SHORT_NAME']
                self.Problem = x
                problematic_order_list.append(json.loads(self.toJSON()))

        return problematic_order_list

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class ExpenseOrder:
    def __init__(self, OrderNo="", CustomerName="", ExpensePrice="", ExpenseReason="", ExpenseDate="",
                 ExpenseDescription="", ExpenseCompany="", ExpenseResponsible="", ExpenseStatus=""):
        self.OrderNo = OrderNo
        self.CustomerName = CustomerName
        self.ExpensePrice = ExpensePrice
        self.ExpenseReason = ExpenseReason
        self.ExpenseDate = ExpenseDate
        self.ExpenseDescription = ExpenseDescription
        self.ExpenseCompany = ExpenseCompany
        self.ExpenseResponsible = ExpenseResponsible
        self.ExpenseStatus = ExpenseStatus

    def make_expense_order_list(self, expenses, orders):
        expense_order_list = []
        num_format = "{} {:.2f}".format
        for x in expenses:
            if x['STATUS'] == 'Açık' or x['STATUS'] == 'Durum Girişi Yapıldı':
                self.OrderNo = x['ORDER_CODE']
                self.ExpenseReason = x['SERVICE_NAME']
                self.ExpenseDate = x['EXPENSE_DATE']
                self.ExpenseDescription = x['MAIL_NOTE']
                self.ExpenseCompany = x['EXPENSE_COMPANY']
                self.ExpenseResponsible = x['RESPONSIBLE']
                self.ExpenseStatus = x['STATUS']
                self.Expense = x
                self.CustomerName = next((x for x in orders if x['ORDER_CODE'] == self.OrderNo), None)[
                    'CUSTOMER_SHORT_NAME']
                if x['CURRENCY'] == "EUR":
                    self.ExpensePrice = num_format("€",x['PRICE'])
                elif x['CURRENCY'] == "USD":
                    self.ExpensePrice = num_format("$",x['PRICE'])
                else:
                    self.ExpensePrice = num_format("₺",x['PRICE'])

                expense_order_list.append(json.loads(self.toJSON()))

        return expense_order_list

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class DelayedOrder:
    def __init__(self, OrderNo="", CustomerName="", ReadyDate="", EstimatedArrivalTime="", DueDate="", Service="",
                 DelayType="", DelayResponsibility="", DelayDescription=""):
        self.OrderNo = OrderNo
        self.CustomerName = CustomerName
        self.ReadyDate = ReadyDate
        self.EstimatedArrivalTime = EstimatedArrivalTime
        self.DueDate = DueDate
        self.Service = Service
        self.DelayType = DelayType
        self.DelayResponsibility = DelayResponsibility
        self.DelayDescription = DelayDescription

    def make_delayed_order_list(self, orders, delays):
        delayed_order_list = []
        for delay in delays:
            self.DelayType = delay['REASON']
            self.DelayResponsibility = delay['RESPONSIBILITY']
            self.DelayDescription = delay['NOTE']
            order = next((x for x in orders if delay['ORDER_CODE'] == x['ORDER_CODE']), None)
            estimated_arrival_time = dt.strptime( order['DATE_ETA'], "%Y-%m-%dT%H:%M:%S")
            due_date = dt.strptime( order['DATE_OG'], "%Y-%m-%dT%H:%M:%S")
            if estimated_arrival_time.date() > due_date.date():
                self.OrderNo = order['ORDER_CODE']
                self.CustomerName = order['CUSTOMER_SHORT_NAME']
                self.ReadyDate = order['DATE_READY']
                self.EstimatedArrivalTime = order['DATE_ETA']
                self.DueDate = order['DATE_OG']
                self.Delay = delay
                self.Order =order
                self.Service = Order.findImportOrExport(self, service_group_code=order['SERVICE_GROUP_CODE'],
                                                        loading_company_info=order["LOADING_COMPANY_INFO"],delivery_company_info=order["DELIVERY_COMPANY_INFO"])

                #gecikme kaydı olsa bile eta>og ise göster
                delayed_order_list.append(json.loads(self.toJSON()))

        return delayed_order_list

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

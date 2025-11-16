import datetime
import comdirect_api.utils
from decimal import Decimal


class DateString():
    """init from YYYY-MM-DD"""

    def __init__(self, s):
        self.date = datetime.datetime.strptime(s, "%Y-%m-%d").date()

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")


# --------------------------- ACCOUNT -----------------------------------------

AccountType = {
    "FX": "Foreign Currency Account",
    "OF": "Options- & Futures Trading Account",
    "CA": "Checking Account",
    "DAS": "Direct Access Savings-Plus Account",
    "CFD": "Contract for Difference Account",
    "SA": "Settlement Account",
    "LLA": "Lombard Loan Account",
}

# TODO: This list is incomplete.
TransactionType = {
    "ATM_WITHDRAWAL": "ATM Withdrawal",
    "DIRECT_DEBIT": "Direct Debit",
    "SECURITIES": "Securities",
    "TRANSFER": "Transfer",
    "INTEREST_DIVIDENDS": "Interest Dividends",
    "BANK_FEES": "Bank fees",
    "UNKNOWN": "Unknown",  # this happens with unbooked transactions
    "XX1": "Saving Plan",
    "XX2": "Investment Saving",
    "XX3": "Bank fees",
    "XX4": "Miscellaneous",
    "XX5": "Cash",
    "XX6": "Interest / Dividends",
    "XX7": "Currency Exchange",
    "XX8": "Cancellation",
    "XX9": "Card Transaction",
    "XXA": "Foreign Currency exchange",
    "XXB": "ATM Withdrawal",
    "XXC": "Savings",
    "XXD": "Standing Order",
}


class AmountValue():
    """ create from JSON REST response

    Example input will look like the following:
    {'unit':'EUR', 'value': '123.45'}
    """

    def __init__(self, json):
        self.unit = json["unit"]
        self.value = Decimal(json["value"])

    def get_amount(self):
        return self.value

    def __str__(self):
        return f"{self.value} {self.unit}"


class Account():
    """ create from JSON REST response

    Example input will look like the following:
        {'accountDisplayId': '12345678901',
        'accountId': '148B8582CFB8F2C0CB8D3E56131891E8',
        'accountType': {'key': 'DAS', 'text': 'Tagesgeld PLUS-Konto'},
        'clientId': 'C87A5216C263B8367CAAE2622EB571F9',
        'creditLimit': {'unit': 'EUR', 'value': '0'},
        'currency': 'EUR',
        'iban': 'DE0820041112345678901'}
    """

    def __init__(self, json):
        self.accountDisplayId = json["accountDisplayId"]
        self.accountId = json["accountId"]
        self.accountType = json["accountType"]["key"]
        assert(self.accountType in AccountType)
        self.clientId = json["clientId"]
        self.creditLimit = AmountValue(json["creditLimit"])
        self.currency = json["currency"]
        self.iban = json["iban"]

    def get_accountId(self):
        return self.accountId

    def __str__(self):
        return f"{AccountType[self.accountType]} ({self.iban})"


class AccountBalance():
    """ create from JSON REST response """

    def __init__(self, json):
        if 'account' in json:
            self.account = Account(json["account"])
        self.accountId = json["accountId"]
        self.availableCashAmount = AmountValue(json["availableCashAmount"])
        self.availableCashAmountEUR = AmountValue(json["availableCashAmountEUR"])
        self.balance = AmountValue(json["balance"])
        self.balanceEUR = AmountValue(json["balanceEUR"])
        assert(self.balanceEUR.unit == "EUR")
        assert(self.availableCashAmountEUR.unit == "EUR")

    def __str__(self):
        return str(self.balance)


class AccountTransaction():
    """ create from JSON REST response

    Example input will look like the following:
        {'amount': {'unit': 'EUR', 'value': '-12.34'},
        'bookingDate': '2020-01-01',
        'bookingStatus': 'BOOKED',
        'creditor': None,
        'deptor': None,
        'directDebitCreditorId': None,
        'directDebitMandateId': None,
        'endToEndReference': None,
        'newTransaction': True,
        'reference': '50C12345A1234567/12345',
        'remittanceInfo': '01Globus TS Forchheim//Forchheim/DE  '
                          '022020-01-01T20:07:16 KFN 0  VJ 1234',
        'remitter': {'holderName': 'Globus Handelshof'},
        'transactionType': {'key': 'DIRECT_DEBIT', 'text': 'Direct Debit'},
        'valutaDate': '2020-01-03'},

    """

    def __init__(self, json):
        self.amount = AmountValue(json["amount"])
        self.bookingDate = DateString(json["bookingDate"]) if json["bookingDate"] else None
        self.bookingStatus = json["bookingStatus"]
        assert(self.bookingStatus in ["BOOKED", "NOTBOOKED"])
        self.booked = (self.bookingStatus == "BOOKED")
        self.creditor = json["creditor"]
        self.deptor = json["deptor"]
        self.directDebitCreditorId = json["directDebitCreditorId"]
        self.directDebitMandateId = json["directDebitMandateId"]
        self.endToEndReference = json["endToEndReference"]
        self.newTransaction = json["newTransaction"]
        self.reference = json["reference"]
        self.remittanceInfo = json["remittanceInfo"]
        self.remitter = json["remitter"]
        self.transactionType = json["transactionType"]["key"]
        # TODO: This will break if you have other transaction types.
        # The problem is that comdirect didn't document the keys.
        # Please report, if you learn what keys there are!
        print(self.transactionType)
        # Tolerate unknown transaction types by mapping them to "Unknown"
        if self.transactionType not in TransactionType:
            TransactionType[self.transactionType] = "Unknown"
        assert(self.transactionType in TransactionType)
        self.valutaDate = json["valutaDate"]  # can be an invalid date!

    def __str__(self):
        return f"{self.bookingDate} {self.amount} {self.transactionType}"


# --------------------------- DEPOT ----------------------------------------


class Depot():
    def __init__(self, json):
        # Some fields may be absent depending on API version
        self.depotId = json.get("depotId")
        self.depotDisplayId = json.get("depotDisplayId")
        self.clientId = json.get("clientId")
        self.depotType = json.get("depotType")
        self.defaultSettlementAccountId = json.get("defaultSettlementAccountId")
        self.settlementAccountIds = json.get("settlementAccountIds")
        self.holderName = json.get("holderName")

    def __str__(self):
        return str(self.depotId)


class DepotBalance():
    def __init__(self, json):
        self.depot = Depot(json.get('depot', {}))
        self.prevDayValue = json.get("prevDayValue", {}).get("value")
        self.currentValue = json.get("currentValue", {}).get("value")
        self.purchaseValue = json.get("purchaseValue", {}).get("value")
        self.profitSincePurchase = json.get("profitLossPurchaseAbs", {}).get("value")
        
        self.profitLossPurchaseRel = json.get("profitLossPurchaseRel")
        self.profitLossPrevDayRel = json.get("profitLossPrevDayRel")
       
    def __str__(self):
        return (
            f'Depot ID: {self.depot.depotId}'
            f'\nDepot Holder: {self.depot.holderName}'
            f'\nPrevious Day Value: {self.prevDayValue}'
            f'\nCurrent Value: {self.currentValue}'
            f'\nPurchase Value: {self.purchaseValue}'
            f'\nProfit Since Purchase: {self.profitSincePurchase}'
            f'\nTotal Performance: {self.profitLossPurchaseRel}'
            f'\n1-Day Performance: {self.profitLossPrevDayRel}'
        )

class DepotPosition():
    def __init__(self, json):
        self.wkn = json.get("wkn")
        self.qty = json.get("quantity", {}).get("value", 0)
        self.purchaseValue = json.get("purchaseValue", {}).get("value", 0)
        self.currentValue = json.get("currentValue", {}).get("value", 0)
        self.profitLossPurchaseAbs = json.get("profitLossPurchaseAbs", {}).get("value")
        self.profitLossPurchaseRel = json.get("profitLossPurchaseRel", 0)
        self.profitLossPrevDayAbs = json.get("profitLossPrevDayAbs", {}).get("value")
        self.profitLossPrevDayRel = json.get("profitLossPrevDayRel", 0)

    def __str__(self):
        return (
            f'WKN: {self.wkn}'
            f'\nQuantity: {self.qty}'
            f'\nPurchase Value: {self.purchaseValue}'
            f'\nCurrent Value: {self.currentValue}'
            f'\nProfit/Loss (Absolute): {self.profitLossPurchaseAbs}'
            f'\nProfit/Loss (Relative): {self.profitLossPurchaseRel}'
            f'\n1-Day Profit/Loss (Absolute): {self.profitLossPrevDayAbs}'
            f'\n1-Day Profit/Loss (Relative): {self.profitLossPrevDayRel}'
        )

# --------------------------- DOCUMENT ----------------------------------------


class DocumentMetadata():
    """ create from JSON REST response

    Example input will look like the following:
    {'alreadyRead': True, 'archived': True, 'dateRead': '2001-12-31', 'predocumentExists': False},
    """

    def __init__(self, json):
        # print(json)
        self.alreadyRead = json["alreadyRead"]
        if self.alreadyRead:
            self.dateRead = DateString(json["dateRead"])
        self.archived = json["archived"]
        self.predocumentExists = json["predocumentExists"]


class Document():
    """ create from JSON REST response

    Example input will look like the following:
    {'advertisement': False,
    'dateCreation': '2001-12-31',
    'deletable': False,
    'documentId': '148B8582CFB8F2C0CB8D3E56131891E8',
    'documentMetaData': {'alreadyRead': True, 'archived': True, 'dateRead': '2001-12-31', 'predocumentExists': False},
    'mimeType': 'text/html',
    'name': 'Wertpapier-Basisinformationen bei Depoteröffnung'}
    """

    def __init__(self, json):
        # print(json)
        self.advertisment = json["advertisement"]
        self.dateCreation = DateString(json["dateCreation"])
        self.deletable = json["deletable"]
        self.documentId = json["documentId"]
        self.documentMetadata = DocumentMetadata(json["documentMetaData"])
        self.mimeType = json["mimeType"]
        self.name = json["name"]

    def get_filename(self):
        fileEnding = ".txt"
        if self.mimeType == "text/html":
            fileEnding = ".html"
        elif self.mimeType == "application/pdf":
            fileEnding = ".pdf"
        return str(self.dateCreation) + "_" + comdirect_api.utils.make_printable(self.name) + fileEnding

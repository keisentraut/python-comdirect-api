import datetime
import comdirect_api.utils
from decimal import Decimal

class DateString():
    """init from YYYY-MM-DD"""

    def __init__(self, s):
        self.date = datetime.datetime.strptime(s, "%Y-%m-%d").date()

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")

AccountType = {
    "FX" : "Foreign Currency Account",
    "OF" : "Options- & Futures Trading Account",
    "CA" : "Checking Account",
    "DAS" : "Direct Access Savings-Plus Account",
    "CFD" : "Contract for Difference Account",
    "SA" : "Settlement Account",
    "LLA" : "Lombard Loan Account",
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

class AccountTransaction():
    pass

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

    def get_balance(self):
        return str(self.balance)






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

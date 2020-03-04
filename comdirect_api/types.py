import datetime
import comdirect_api.utils

class DateString():
    """init from YYYY-MM-DD"""
    def __init__(self, s):
        self.date = datetime.datetime.strptime(s, "%Y-%m-%d").date()

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")

class DocumentMetadata():
    """ create from JSON REST response
    
    It will look like the following: 
    {'alreadyRead': True, 'archived': True, 'dateRead': '2001-12-31', 'predocumentExists': False},
    """
    def __init__(self, json):
        #print(json)
        self.alreadyRead  = json["alreadyRead"]
        if self.alreadyRead:
            self.dateRead     = DateString(json["dateRead"])
        self.archived     = json["archived"]
        self.predocumentExists = json["predocumentExists"]

class Document():
    """ create from JSON REST response

    It will look like the following:
    {'advertisement': False,
    'dateCreation': '2001-12-31',
    'deletable': False,
    'documentId': '148B8582CFB8F2C0CB8D3E56131891E8',
    'documentMetaData': {'alreadyRead': True, 'archived': True, 'dateRead': '2001-12-31', 'predocumentExists': False},
    'mimeType': 'text/html',
    'name': 'Wertpapier-Basisinformationen bei Depoteröffnung'}
    """
    def __init__(self, json):
        #print(json)
        self.advertisment = json["advertisement"]
        self.dateCreation = DateString(json["dateCreation"])
        self.deletable    = json["deletable"]
        self.documentId   = json["documentId"]
        self.documentMetadata = DocumentMetadata(json["documentMetaData"])
        self.mimeType     = json["mimeType"]
        self.name         = json["name"]
    
    def get_filename(self):
        fileEnding = ".txt"
        if self.mimeType == "text/html":
            fileEnding = ".html"
        elif self.mimeType == "application/pdf":
            fileEnding = ".pdf"
        return str(self.dateCreation) + "_" + comdirect_api.utils.make_printable(self.name) + fileEnding

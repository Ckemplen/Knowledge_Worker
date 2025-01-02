import requests

import json
import core.config as config


class DocumentAnalysisConnector:
    def __init__(self):
        self.FLOW_ENDPOINT = config.DOCANALYSIS_ENDPOINT
        self.FLOW_HOST =  self.FLOW_ENDPOINT.split(":443")[0]

    def process_document(self, document_text):

        data = {
            'document_text': document_text,
        }

        try:
            with requests.post(
                self.FLOW_ENDPOINT, data=data
            ) as get_flow_response:
                print(get_flow_response)
            
                return json.loads(get_flow_response.content)

        except Exception as e:
            print("Exception...")
            print(e)

        
import requests
import abc
import uuid
import json
import tiktoken
import core.config as config

from typing import TypedDict, List, Dict

class DASubtopic(TypedDict):
    name: Dict[str, str]
    description: Dict[str, str]
    prevalence: Dict[str, str]

class DATopic(TypedDict):
    name: Dict[str, str]
    description: Dict[str, str]
    prevalence: Dict[str, str]
    subtopics: List[DASubtopic]

class DAEntity(TypedDict):
    name: Dict[str, str]
    description: Dict[str, str]
    prevalence: Dict[str, str]

class DocumentAnalysis(TypedDict):
    topics: List[DATopic]
    entities: List[DAEntity]
    summary: Dict[str, str]

class DocumentAnalysisResponse(TypedDict):
    document_analysis: DocumentAnalysis

class CanonicalEntityResponseItem(TypedDict):
    name: str
    description: str
    canonical_entity_id: int
    raw_entity_ids: List[int]

CanonicalEntityResponse = List[CanonicalEntityResponseItem]


class AbstractConnector(abc.ABC):
    def __init__(self):
        self.token_count = {
            'total': {
                'input': 0,
                'output': 0
            },
            }

    def generate(self, **kwargs):
        generation_uuid = uuid()

        new_input_tokens = self.calculate_tokens(**kwargs)
        result = self._generate(**kwargs)
        new_output_tokens = self.calculate_tokens(result=result)

        self.token_count['total']['input'] += new_input_tokens
        self.token_count['total']['output'] += new_output_tokens
        self.token_count[generation_uuid]['input'] += new_input_tokens
        self.token_count[generation_uuid]['output'] += new_output_tokens

        return self._generate(**kwargs)
    

    def calculate_tokens(self, **kwargs) -> int:
        input_str = json.dumps(kwargs)
        encoding = tiktoken.encoding_for_model('gpt-4o-2024-05-13')
        num_tokens = len(encoding.encode(input_str))
        return num_tokens


    @abc.abstractmethod
    def _generate(self, entity):
        raise NotImplementedError

class FakeDocumentAnalysisConnector(AbstractConnector):
    def _generate(self, **kwargs):
        response: DocumentAnalysisResponse = {
            'document_analysis': {
                'entities': [{
                    'description': 'Fake entity description',
                    'name': 'Fake entity name',
                    'prevalence': 5
                }],
                'topics': [{
                    'description': 'Fake topic description',
                    'name': 'Fake topic name',
                    'prevalence': 4,
                    'subtopics': [{
                        'description': 'Fake subtopic description',
                        'name': 'Fake subtopic name',
                        'prevalence': 6
                    }]
                }],
                'summary': "Summary of document."
            }
        }
        return response
    
class DocumentAnalysisConnector(AbstractConnector):
    def __init__(self):
        self.FLOW_ENDPOINT = config.DOCANALYSIS_ENDPOINT
        self.FLOW_HOST =  self.FLOW_ENDPOINT.split(":443")[0]

    def _generate(self, **kwargs):
        return self.process_document(**kwargs)

    def process_document(self, document_text) -> DocumentAnalysisResponse:

        data = {
            'document_text': document_text,
        }

        try:
            with requests.post(
                self.FLOW_ENDPOINT, data=data
            ) as get_flow_response:
                print(get_flow_response)
                data: DocumentAnalysisResponse = json.loads(get_flow_response.content)
                return data

        except Exception as e:
            print("Exception...")
            print(e)


class CanonicalEntityConsolidationConnector(AbstractConnector):
    """
    Example usage:
    response = CanonicalEntityConsolidationConnector().consolidate(raw_entities=raw_entities)
    """
    def __init__(self):
        self.FLOW_ENDPOINT = config.CANONICAL_ENTITIES_CONSOLIDATION_ENDPOINT
        self.FLOW_HOST =  self.FLOW_ENDPOINT.split(":443")[0]

    def _generate(self, **kwargs):
        return self.consolidate(**kwargs)

    def consolidate(
            self, raw_entities: List[Dict], 
            existing_canonical_entities: List[Dict]=[]
            ) -> List[CanonicalEntityResponseItem]:
        data = {
            'raw_entities': raw_entities,
            'existing_canonical_entities': existing_canonical_entities
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                self.FLOW_ENDPOINT, 
                data=json.dumps(data), 
                headers=headers
            )
            print(response)
            data: List[CanonicalEntityResponseItem] = response.json()
            return data

        except Exception as e:
            print("Exception...")
            print(e)


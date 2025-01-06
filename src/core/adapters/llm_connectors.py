import requests
import abc
import json
import tiktoken
import datetime
import logging
import core.config as config

from typing import TypedDict, List, Dict, NotRequired

logging.basicConfig(level=logging.INFO)

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
    canonical_entity_id: NotRequired[int]
    raw_entity_ids: List[int]

CanonicalEntityResponse = List[CanonicalEntityResponseItem]


class AbstractConnector(abc.ABC):
    token_count = {
        'total': {
            'input': 0,
            'output': 0
        },
    }

    def __init__(self):
        pass

    def generate(self, **kwargs):
        result = self._generate(**kwargs)

        try:
            # Generate a unique key using the concrete class's name and a datetime stamp
            generation_uuid = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}-{self.__class__.__name__}"

            new_input_tokens = self.calculate_tokens(**kwargs)
            new_output_tokens = self.calculate_tokens(result=result)

            # Update class token count
            AbstractConnector.token_count['total']['input'] += new_input_tokens
            AbstractConnector.token_count['total']['output'] += new_output_tokens
            AbstractConnector.token_count[generation_uuid] = {'input': new_input_tokens, 'output': new_output_tokens}

            # Log the update
            logging.info(f"Updated token count for {generation_uuid}: {AbstractConnector.token_count[generation_uuid]}")
            logging.info(f"Total token count: {AbstractConnector.token_count['total']}")

            print(f"Updated token count for {generation_uuid}: {AbstractConnector.token_count[generation_uuid]}")
            print(f"Total token count: {AbstractConnector.token_count['total']}")

        except Exception as e:
            logging.error("Error calculating token usage.")
            logging.error(e)
            print("Error calculating token usage.")
            print(e)

        return result
    

    def calculate_tokens(self, **kwargs) -> int:
        input_str = json.dumps(kwargs)
        encoding = tiktoken.encoding_for_model('gpt-4o-2024-05-13')
        num_tokens = len(encoding.encode(input_str))
        return num_tokens


    @abc.abstractmethod
    def _generate(self, entity):
        raise NotImplementedError

class FakeDocumentAnalysisConnector(AbstractConnector):
    def __init__(self):
        super().__init__()

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
        super().__init__()
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
    response = CanonicalEntityConsolidationConnector().consolidate(raw_entities, existing_canonical_entities)
    """
    def __init__(self):
        super().__init__()
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


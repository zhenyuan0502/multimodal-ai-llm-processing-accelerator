import json
import logging
import os
from typing import Optional

import azure.functions as func
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from src.components.content_understanding_client import (
    AzureContentUnderstandingClient,
    get_existing_analyzer_ids,
)
from src.helpers.common import MeasureRunTime
from src.helpers.content_understanding import (
    cu_fields_dict_to_markdown,
    draw_fields_on_imgs,
    enrich_extracted_cu_fields,
)
from src.helpers.data_loading import load_visual_obj_bytes_to_pil_imgs_dict
from src.helpers.image import pil_img_to_base64_bytes, resize_img_by_max, rotate_img_pil
import create_content_understanding_analyzers as create_cu_analyzer


load_dotenv()

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

bp_create_content_understanding_schema = func.Blueprint()
FUNCTION_ROUTE = "create_content_understanding_schema"

# Load environment variables
CONTENT_UNDERSTANDING_ENDPOINT = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT")

@bp_create_content_understanding_schema.route(route=FUNCTION_ROUTE)
def create_content_understanding_schema(
    req: func.HttpRequest,
) -> func.HttpResponse:
    logging.info(f"Python HTTP trigger function `{FUNCTION_ROUTE}` received a request.")

    try:
        ids = create_cu_analyzer.create_config_analyzer_schemas(True)
        logging.info(f"Created Content Understanding analyzers: {ids}.")
        
        return func.HttpResponse(
            body=json.dumps(ids),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as _e:
        logging.error(f"Error creating Content Understanding analyzers: {_e}")
        return func.HttpResponse(
            body=json.dumps({"error": str(_e)}),
            mimetype="application/json",
            status_code=500,
        )

import json
import logging
import uuid

from common.response import get_standard_response
from live_location.services.core import svc_live_location_add_location_ping
from rest_framework import generics
from rest_framework.permissions import AllowAny


class LocationTrackingView(generics.GenericAPIView):
    logger = logging.getLogger(__name__ + ".LocationTrackingView")
    permission_classes = (AllowAny,)

    def _get_payload(self, request) -> dict:
        """Safely extracts and normalizes the payload into a pure Python dict."""
        
        # 1. Handle standard URL-encoded form data (QueryDict)
        if hasattr(request.data, "dict"):
            # Edge case: Devices sending raw JSON but with URL-encoded headers
            # DRF interprets the entire JSON string as a single key with an empty value.
            if len(request.data) == 1:
                key = list(request.data.keys())[0]
                if key.strip().startswith(("{", "[")):
                    try:
                        return json.loads(key)
                    except json.JSONDecodeError:
                        pass
            
            # Normal URL-encoded data: flatten the QueryDict to a standard dict
            return request.data.dict()

        # 2. Handle standard JSON data (already parsed to dict by DRF)
        if isinstance(request.data, dict):
            return request.data

        # 3. Ultimate fallback: try parsing the raw body
        try:
            body_str = request.body.decode("utf-8").strip()
            if body_str.startswith(("{", "[")):
                return json.loads(body_str)
        except Exception:
            pass

        return {}

    def post(self, request, tracker_client: str, tracking_id: uuid.UUID):
        request_data = self._get_payload(request)
        error, response = svc_live_location_add_location_ping(
            tracker_client=tracker_client, tracking_id=tracking_id, request_data=request_data
        )
        return get_standard_response(error, response)

import json
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse, QueryDict, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .models import Czlowiek
from .forms import CzlowiekForm
import logging

logger = logging.getLogger(__name__)

def cors_response(response):
    """Add CORS headers to response"""
    response["Access-Control-Allow-Origin"] = "*"  # Allow all origins
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
    return response

class PersonView(View):
    """Base class for person views with common functionality"""
    model = Czlowiek
    form_class = CzlowiekForm

    def render_response(self, data, status=200):
        """Standardize JSON response format"""
        response = JsonResponse(data, status=status)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
        return response

    def handle_exception(self, exc, message):
        """Standardize exception handling"""
        if isinstance(exc, ObjectDoesNotExist):
            return self.render_response({
                'success': False,
                'message': f'Resource not found'
            }, status=404)
        
        logger.exception(message)
        return self.render_response({
            'success': False,
            'message': str(exc)
        }, status=500)

    def parse_json_body(self, request):
        """Parse and validate JSON request body"""
        try:
            if isinstance(request.body, bytes):
                return json.loads(request.body.decode('utf-8'))
            return json.loads(request.body)
        except json.JSONDecodeError:
            return None

@method_decorator(csrf_exempt, name='dispatch')
class PersonListView(PersonView):
    """Handle list and create operations"""
    
    def get(self, request):
        """Get list of all people"""
        try:
            people = self.model.objects.all()
            return self.render_response({
                'success': True,
                'data': list(people.values('id', 'imie', 'nazwisko'))
            })
        except Exception as e:
            return self.handle_exception(e, "Error fetching people list")

    def post(self, request):
        """Create new person"""
        try:
            data = self.parse_json_body(request) if request.content_type == 'application/json' else request.POST
            
            if data is None:
                return self.render_response({
                    'success': False,
                    'message': 'Invalid JSON format'
                }, status=400)

            form = self.form_class(data)
            if form.is_valid():
                person = form.save()
                return self.render_response({
                    'success': True,
                    'message': 'Person created successfully',
                    'data': {
                        'id': person.id,
                        'imie': person.imie,
                        'nazwisko': person.nazwisko,
                    }
                })
            
            return self.render_response({
                'success': False,
                'message': 'Invalid form data',
                'errors': form.errors
            }, status=400)
            
        except Exception as e:
            return self.handle_exception(e, "Error creating person")

@method_decorator(csrf_exempt, name='dispatch')
class PersonDetailView(PersonView):
    def put(self, request, id):
        """Update person"""
        try:
            person = self.model.objects.get(pk=id)
            
            # Debug logging
            logger.debug(f"Request content type: {request.content_type}")
            logger.debug(f"Request body: {request.body}")
            logger.debug(f"Request GET params: {request.GET}")
            
            # Try to get data from multiple sources
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    data = None
            else:
                # Handle form-data or query parameters
                data = request.GET.dict()  # Get query parameters
                if not data:  # If no query parameters, try POST/PUT data
                    data = QueryDict(request.body).dict()
            
            logger.debug(f"Processed data: {data}")
            
            if not data:
                return self.render_response({
                    'success': False,
                    'message': 'No data received',
                    'debug': {
                        'content_type': request.content_type,
                        'body': request.body.decode('utf-8'),
                        'GET': dict(request.GET),
                    }
                }, status=400)
            
            # Create form instance with both POST data and files
            form = self.form_class(data, instance=person)
            logger.debug(f"Form data: {form.data}")
            
            if form.is_valid():
                logger.debug("Form is valid")
                updated_person = form.save()
                return self.render_response({
                    'success': True,
                    'message': 'Person updated successfully',
                    'data': {
                        'id': updated_person.id,
                        'imie': updated_person.imie,
                        'nazwisko': updated_person.nazwisko,
                    }
                })
            
            logger.debug(f"Form errors: {form.errors}")
            # Return form errors in a cleaner format
            return self.render_response({
                'success': False,
                'message': 'Validation failed',
                'errors': form.errors,
                'debug': {
                    'received_data': data,
                    'form_data': form.data
                }
            }, status=400)
            
        except Exception as e:
            logger.exception(f"Error updating person {id}")
            return self.render_response({
                'success': False,
                'message': str(e)
            }, status=500)
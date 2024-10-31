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

@method_decorator(csrf_exempt, name='dispatch')
class PersonView(View):
    """Base class for person-related views"""
    model = Czlowiek
    form_class = CzlowiekForm
    template_name = 'api_response.html'

    def options(self, request, *args, **kwargs):
        """Handle preflight CORS requests"""
        response = HttpResponse()
        return cors_response(response)

    def render_response(self, data, status=200):
        """Render response based on the request type and origin"""
        is_form_submit = (
            'text/html' in self.request.META.get('HTTP_ACCEPT', '') and 
            self.request.method == 'POST' and
            data.get('success', False)
        )

        if 'text/html' in self.request.META.get('HTTP_ACCEPT', ''):
            response = render(
                self.request,
                self.template_name,
                {'json_response': json.dumps(data, indent=2, ensure_ascii=False)},
                status=status
            )
        else:
            response = JsonResponse(data, status=status, safe=False)
        
        return cors_response(response)

    def handle_exception(self, e, custom_message=None):
        """Centralized exception handling"""
        if isinstance(e, ObjectDoesNotExist):
            return self.render_response({
                'success': False,
                'message': custom_message or str(e)
            }, status=404)
        
        logger.exception(custom_message or "An error occurred")
        return self.render_response({
            'success': False,
            'message': str(e)
        }, status=500)

# ... rest of your views remain the same ...

@method_decorator(csrf_exempt, name='dispatch')
class PersonListView(PersonView):
    """Handle list and create operations"""
    
    def get(self, request):
        """Get list of all people"""
        try:
            people = self.model.objects.all()
            return self.render_response({
                'success': True,
                'data': list(people.values())
            })
        except Exception as e:
            return self.handle_exception(e, "Error fetching people list")

    def post(self, request):
        """Create new person"""
        try:
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    return self.render_response({
                        'success': False,
                        'message': 'Invalid JSON format'
                    }, status=400)
                
                form_data = QueryDict('', mutable=True)
                form_data.update(data)
                
            elif not request.POST and request.GET:
                form_data = QueryDict('', mutable=True)
                form_data.update({
                    'imie': request.GET.get('imie', ''),
                    'nazwisko': request.GET.get('nazwisko', '')
                })
            else:
                form_data = request.POST

            form = self.form_class(form_data)
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
    """Handle individual person operations"""
    
    def get(self, request, id):
        """Get person details"""
        try:
            person = self.model.objects.get(pk=id)
            return self.render_response({
                'success': True,
                'data': {
                    'id': person.id,
                    'imie': person.imie,
                    'nazwisko': person.nazwisko,
                }
            })
        except Exception as e:
            return self.handle_exception(e, f"Error fetching person {id}")

    def put(self, request, id):
        """Update person"""
        try:
            person = self.model.objects.get(pk=id)
            form = self.form_class(request.POST, instance=person)
            if form.is_valid():
                updated_person = form.save()
                return self.render_response({
                    'success': True,
                    'message': 'Person updated successfully',
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
            return self.handle_exception(e, f"Error updating person {id}")

    def delete(self, request, id):
        """Delete person"""
        try:
            person = self.model.objects.get(pk=id)
            person.delete()
            return self.render_response({
                'success': True,
                'message': 'Person deleted successfully'
            })
        except Exception as e:
            return self.handle_exception(e, f"Error deleting person {id}")
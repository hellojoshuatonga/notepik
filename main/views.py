# Python
import logging
import datetime

# Django
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import utc
from django.conf import settings
from django.db.models import Case, When, F, DateTimeField

# Custom
from main.models import Note, Category, EncodedUrl
from main.forms import NoteForm, KeyForm, SearchForm
from main.utils import UrlShortener

logger = logging.getLogger(__name__)
UserModel = get_user_model()

def index(request):
    """" 
    Index view
    """
    logger.info("Got a request for index page");
    notes = Note.objects.all()[:settings.REST_FRAMEWORK.get('PAGE_SIZE')]

    # context to use in templates
    context = dict(notes=notes, key_not_exist=False)
    
    form = NoteForm()
    key_form = KeyForm()
    search_form = SearchForm()

    # add form to context
    context['form'] = form
    context['key_form'] = key_form
    context['search_form'] = search_form

    return render(request, 'main/index.html',
            context)

def vault(request, encoded_url):
    encoded_obj = EncodedUrl.objects.get_or_none(encoded_url=encoded_url,
            expiration_date__gte=datetime.datetime.now(tz=utc))
    if encoded_obj is None:
        raise Http404

    # decoded_user_id = UrlShortener.decode(encoded_obj.encoded_url,
            # encoded_obj.salt)

    # user = UserModel.objects.get(pk=decoded_user_id)

    # Form for searching notes from db using ajax
    search_form = SearchForm()

    user = encoded_obj.user

    # Combine all the notes created and reposted
    notes = user.notes_created.all() | user.notes_reposted.all()

    # Sort it! :)
    notes = notes.annotate(newest_in_vault=Case(When(notereposter__isnull=False,
        then=F("notereposter__date_added")), default=F("date_created"),
        output_field=DateTimeField()))
    notes = notes.order_by('-newest_in_vault')

    context = dict(notes=notes.all()[:settings.REST_FRAMEWORK.get('PAGE_SIZE')], search_form=search_form)

    return render(request, 'main/vault.html', context)

# Python
import logging
import datetime

# Django
from django.http import Http404
from django.utils.http import urlunquote
from django.contrib.auth import get_user_model
from django.utils.timezone import utc
from django.conf import settings
from django.db.models import Count, Case, When, F, Q, DateTimeField

# Rest framework
from rest_framework import status
from rest_framework import generics, viewsets
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse as rest_reverse
from rest_framework.decorators import detail_route, list_route
from rest_framework.settings import api_settings
from rest_framework.pagination import LimitOffsetPagination

# Rest framework jwt
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

# Custom
from main.models import Note, Category, EncodedUrl, NotepikUser, NoteReposter
from main.serializers import NoteSerializer, CategorySerializer
from main.serializers import NotepikUserSerializer
from main.permissions import IsAuthorOrReadOnly
from main.utils import UrlShortener
from main.paginations import CategoryInfoPagination


logger = logging.getLogger(__name__)
UserModel = get_user_model()


class APIRoot(APIView):
    """ 
    Api root view. This view will list all the api's we have
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        return Response(dict(
            notes=rest_reverse('main:note-list', request=request, format=format),
            notecategories=rest_reverse('main:category-list', request=request,
                format=format),
            notepikusers=rest_reverse('main:notepikuser-list', request=request,
                format=format),
            ))


class NoteViewSet(viewsets.ModelViewSet):
    """
    An api view for Note model
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
            IsAuthorOrReadOnly,)
    # authentication_classes = (authentication.SessionAuthentication,
            # JSONWebTokenAuthentication,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def create(self, request):
        note = Note()
        note.note = request.data.get('note')
        note.author = request.user

        # Check if the length of category is greater than 15, if it is then we return error
        categories = note.extract_categories()
        for category in categories:
            if len(category) > 15:
                return Response(dict(result='category length greater than 15'),
                        status=status.HTTP_400_BAD_REQUEST)

        note.save()
        serialized = NoteSerializer(note, context=dict(request=request))
        return Response(serialized.data, status=status.HTTP_201_CREATED)


    @detail_route()
    def add_to_vault(self, request, *args, **kwargs):
        """
        A view for adding reposter of notes
        """
        try:
            # Check the user is authenticated
            if not request.user.is_authenticated():
                return Response(dict(result='not-authenticated'), status=
                        status.HTTP_403_FORBIDDEN)

            # Get the note object 
            note = self.get_object()

            # If the author of the note and requesting user is same then error
            if note.author.pk != request.user.pk:
                # If they're already in the respoters list then send 400 code else add
                if note.reposters.is_already_added(request.user):
                    return Response(dict(result="already added"), status=
                            status.HTTP_400_REQUEST)
                else:
                    NoteReposter.objects.create(note=note, user=request.user)
            else:
                return Response(dict(result="you are the author"), status=
                        status.HTTP_400_BAD_REQUEST)

            # Success adding to vault
            logger.info("Reposter added in note: {}:{}".format(note.note,
                request.user.email))
            return Response(dict(result='success'), status=status.HTTP_200_OK)
        except Exception as error:
            return Response(dict(result=str(error)), status=
                    status.HTTP_400_BAD_REQUEST)

    @detail_route()
    def remove_from_vault(self, request, *args, **kwargs):
        """ 
        Remove the note from vault
        """
        try:
            # Only authenticated user
            if not request.user.is_authenticated():
                return Response(dict(result="not-authenticated"), status=
                        status.HTTP_403_FORBIDDEN)

            note = self.get_object()

            temp_author = UserModel.objects.get_or_none(email=
                    settings.TEMPORARY_AUTHOR_EMAIL)

            # If the requesting user is the author of the note then we will
            # assign the note author to temporary user
            if note.author.pk == request.user.pk:
                
                # If the note don't have any reposters then we wil ldelete it from database
                if note.reposters.count() == 0:
                    logger.debug("Deleting note from database: {}".format(note.id))
                    note.delete()
                    return Response(dict(result="removed from vault of author"),
                            status=status.HTTP_200_OK)

                if temp_author is None:
                    temp_author = UserModel.objects.create_user(email=
                            settings.TEMPORARY_AUTHOR_EMAIL, password=
                            settings.TEMPORARY_AUTHOR_PASSWORD)
                note.author = temp_author
                note.save()
                logger.info("Author remove from note: {}:{}".format(note.note,
                    request.user.email))
                return Response(dict(result="removed from vault of author"),
                        status=status.HTTP_200_OK)
            else:
                if note.author == temp_author and note.reposters.count() == 1\
                    and note.reposters.get_or_none(email=request.user.email) is not None:
                    logger.debug("Deleting note from database: {}".format(note.id))
                    note.delete()
                    return Response(dict(result="removed from vault of reposter"),
                            status=status.HTTP_200_OK)
                else:
                    if note.reposters.is_already_added(request.user):
                        NoteReposter.objects.get(note=note, user=request.user).delete()
                        logger.info("Reposter remove from note: {}:{}".format(note.note,
                            request.user.email))
                        return Response(dict(result="removed from vault"), status=
                                status.HTTP_200_OK)
                    else:
                        return Response(dict(result="not in your vault"), status=
                                status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response(dict(result=str(error)), status=
                    status.HTTP_400_BAD_REQUEST)

    @list_route(methods=["get"], permission_classes=[permissions.AllowAny])
    def get_vault_notes(self, request):
        """ 
        Get notes of specified vault page
        """
        try:
            # Get encoded url
            encoded_url = request.query_params.get("encoded_url")

            logger.debug("Encoded url: " + encoded_url)

            if encoded_url is None:
                raise ValueError("Encoded url is None")

            # Get the encode url object from db
            encoded_url_obj = EncodedUrl.objects.get(encoded_url=encoded_url)

            # Extract the user from the encoded url
            user = encoded_url_obj.user

            # get notes
            notes = Note.objects.filter(Q(author=user) | Q(reposters=user))
            # notes = Note.objects.filter(Q(notereposter__user=user) | 
                    # Q(author=user))

            # Sort it! :)
            # notes = notes.annotate(newest_in_vault=Case(When(notereposter__isnull=False,
                # then=F("notereposter__date_added")), default=F("date_created"),
                # output_field=DateTimeField()))
            # notes = notes.order_by('-newest_in_vault')

            logger.debug("Notes found: {}".format(notes.count()))

            # Paginate
            page = self.paginate_queryset(notes)

            if page is not None:
                logger.info("Page is not none")
                serializer = self.get_serializer(page, many=True, context=dict(
                    request=request))
                return self.get_paginated_response(serializer.data)

            logger.info("Page is none")
            serializer = self.get_serializer(notes, many=True, context=dict(
                request=request))
            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as error:
            logger.error("Get vault notes error: {}".format(error))
            return Response(dict(result=str(error)), status.HTTP_400_BAD_REQUEST)


    @list_route(methods=["get"], permission_classes=[permissions.AllowAny])
    def search(self, request):
        """ 
        Search notes by note, category, date
        """
        try:
            # Get query
            query = urlunquote(request.query_params.get("query"))

            if query is None or query == "":
                raise ValueError("Query is none")

            # Regex: query*
            # NOTE: No need to add * if you're using postgresl
            # query = query + "*"
            logger.debug("Query: {}".format(query))

            # Check if searching using category or note
            if (query[0] == "#"):
                # Searching using category
                logger.info("Searching using category: " + query)
                notes = Note.objects.filter(categories__category__icontains= \
                        query.replace('#', '', 1))
            else:
                # Searching using notes, etc
                logger.info("Searching using notes, etc: " + query)
                notes = Note.objects.filter(note__icontains=query)

            logger.info("Notes found: {}".format(notes.count()))

            # Paginate the results
            page = self.paginate_queryset(notes)

            if page is not None:
                logger.info("Page is not none")
                serializer = self.get_serializer(page, many=True, context=dict(
                    request=request))
                return self.get_paginated_response(serializer.data)

            # Page is none. Last page
            logger.info("Page is none")
            serializer = self.get_serializer(notes, many=True, context=dict(
                request=request))
            return Response(serializer.data, status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            logger.error("Search notes error: {}".format(error))
            return Response(dict(result=str(error)), status.HTTP_400_BAD_REQUEST)



    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    View for Category model
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryInfoPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (JSONWebTokenAuthentication,)


    @list_route(methods=["get"], permission_classes=[permissions.AllowAny])
    def get_info(self, request):
        try: 
            logger.info("Getting information of category")

            # Extract query
            query = urlunquote(request.query_params.get("query")) 

            if query is None or query == "":
                raise ValueError("Query is null")

            # NOTE: If you're using postgresql, no need to add * in query
            # query = query + "*"
            if query[0] == '#':
                # Remove the first occurence of pound sign.
                query = query.replace('#', '', 1) 
            logger.debug("Query: {}".format(query))

            # Get all notes with category of query.
            notes = Note.objects.filter(categories__category__icontains=query)
            logger.debug("Notes count: {}".format(notes.count()))
            # Remove * regex from query so we can exclude it.
            query_without_re = query[::-1].replace('*', '', 1)[::-1]
            # Get top 5 most used categories in the extracted notes above.
            categories = Category.objects.filter(notes__in=notes) \
                    .annotate(score=Count('notes')).exclude(category= \
                    query_without_re).order_by('-score', '-date_created')[:5]
            logger.debug('Categories count: {}'.format(categories.count()))

            # Paginate
            page = self.paginate_queryset(categories)

            if page is not None:
                logger.debug("Page is not none")
                serializer = self.get_serializer(page, many=True, context=dict(
                    request=request))
                return self.paginator.get_paginated_response(serializer.data, notes.count())

            logger.debug("Page is none")
            serializer = self.get_serializer(categories, many=True, context=dict(
                request=request))
            return Response(serializer.data, status.HTTP_200_OK)

        except Exception as error:
            logger.error("Error getting category information: {}, {}".format(
                query, error))
            return Response(dict(result=str(error)), status.HTTP_400_BAD_REQUEST)





class NotepikUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View for our User model
    """
    queryset = NotepikUser.objects.all()
    serializer_class = NotepikUserSerializer

class VaultPage(APIView):
    """ 
    Generate an url encoded for vault page.
    The vault page will expire after 1 day
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        """ 
        Exchange key for his/her vault encoded url
        """
        user = UserModel.objects.get_or_none(key=request.data.get('key'))
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        
        try: 
            # Get the encoded url of the user
            encoded_url_obj = EncodedUrl.objects.get(user=user)
            
            # If it's not expired then we will get the encoded url and salt
            if encoded_url_obj.expiration_date >= datetime.datetime.now(tz=utc):
                encoded_url = encoded_url_obj.encoded_url
                salt = encoded_url_obj.salt
            else:
                # If it's expired, Renew it.
                encoded_url, salt = UrlShortener.encode(user.pk)
                encoded_url_obj.encoded_url = encoded_url
                encoded_url_obj.salt = salt
                encoded_url_obj.expiration_date = datetime.datetime.now(tz=utc)\
                                        + datetime.timedelta(hours=1)
                encoded_url_obj.save()

        except EncodedUrl.DoesNotExist:
            # If user doesn't have any encoded url, we will create a new one
            encoded_url, salt = UrlShortener.encode(user.pk) 
            EncodedUrl.objects.create(user=user, encoded_url=encoded_url,
                    salt=salt)

        return Response(dict(
                encoded_url=encoded_url
                ), status=status.HTTP_200_OK)


class SearchVault(APIView):
    """
    Search notes inside of a vault page 

    @params vault_url search notes for this vault page
    @params query search query. can be note, category, date, reposted, created, todo

    @return data json of notes 
    """
    permission_classes = (permissions.AllowAny,)

    # Pagination code is copied from :
    # http://stackoverflow.com/questions/29071312/pagination-in-django-rest-framework-using-api-view
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request, format=None):
        try:
            # Get the query parameter
            query = urlunquote(request.query_params.get("query"))
            encoded_url = request.query_params.get("encoded_url")

            if query is None or query == "":
                return Response(dict(result="Need query"), 
                        status.HTTP_400_BAD_REQUEST)

            if encoded_url is None or encoded_url == "":
                return Response(dict(result="Need encoded_url"), 
                        status.HTTP_400_BAD_REQUEST)

            # Regex: query*
            # query = query + "*" 

            logger.debug("Query: {}".format(query))
            logger.debug("Encoded_url: {}".format(encoded_url))

            # Get encoded url object of passed encoded_url
            encoded_url_obj = EncodedUrl.objects.get(encoded_url=encoded_url)

            # Get user of the encoded url
            user = encoded_url_obj.user
            logger.debug("User email: {}".format(user.email))

            # Check if searching using category or not
            if (query[0] == "#"):
                # Searching using category
                query = query.replace('#', '', 1)
                logger.info("Searching using category: " + query)

                # get notes
                notes = Note.objects.filter(Q(author=user, \
                        categories__category__icontains=query) | Q(reposters=user, \
                        categories__category__icontains=query))
            else:
                # Searching using notes, etc
                logger.info("Searching using notes, etc: " + query)
                # Get notes created and reposted of user
                notes = Note.objects.filter(Q(author=user, note__icontains= \
                        query) | Q(reposters=user, note__icontains=query))
            
            logger.debug("Count of notes found: {}".format(notes.count()))

            # Paginate!
            page = self.paginate_queryset(notes)

            if page is not None:
                serializer = NoteSerializer(page, many=True, context=dict(
                    request=request))
                return self.get_paginated_response(serializer.data)

            # Serialize the notes
            serializer = NoteSerializer(notes, many=True, context=dict(
                request=request))
            return Response(serializer.data, status.HTTP_200_OK)
        except EncodedUrl.DoesNotExist as error:
            logger.error(str(error))
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            logger.error(str(error))
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator


    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, 
                self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

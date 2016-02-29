# Rest framework
from rest_framework import serializers

# Custom
from main.models import Note, Category, NotepikUser
from main.templatetags.custom_filters import timeago
from main.serializer_fields import CategoriesField






class NoteSerializer(serializers.HyperlinkedModelSerializer):
    """
    A serializer for Note model
    """
    reposters_count = serializers.ReadOnlyField(source='reposters.count')
    # author = serializers.HyperlinkedRelatedField(view_name=
            # 'main:notepikuser-detail', queryset=NotepikUser.objects.all())
    author = serializers.HyperlinkedRelatedField(view_name=
            'main:notepikuser-detail', read_only=True)
    reposters = serializers.HyperlinkedRelatedField(view_name=
            'main:notepikuser-detail', many=True, read_only=True)
    # categories = serializers.HyperlinkedRelatedField(view_name=
    categories = CategoriesField(required=False, many=True, read_only=True)
    # categories = CategorySerializer(many=True, read_only=True)
            # 'main:category-detail', many=True, read_only=True)

    def to_representation(self, instance):
        data = super(NoteSerializer, self).to_representation(instance)

        data['date_modified_timeago'] = timeago(instance.date_modified)
        data['date_created_timeago'] = timeago(instance.date_created)

        return data

    class Meta:
        model = Note
        fields = ('id', 'date_modified', 'date_created', 'note', 'author',
                'reposters', 'reposters_count', 'categories')


        
class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """ 
    Serializer for Category model
    """
    notes = serializers.HyperlinkedRelatedField(view_name='main:note-detail',
            many=True, read_only=True)


    class Meta:
        model = Category
        fields = ('id', 'date_modified','date_created', 'category', 'notes')



class NotepikUserSerializer(serializers.HyperlinkedModelSerializer):
    """ 
    Serializer for NotepikUser (default user model)
    """
    notes_created = serializers.HyperlinkedRelatedField(view_name=
            'main:note-detail', many=True, read_only=True)
    notes_reposted = serializers.HyperlinkedRelatedField(view_name=
            'main:note-detail', many=True, read_only=True)

    class Meta:
        model = NotepikUser
        fields = ('id', 'date_modified' ,'email', 'notes_created',
                'notes_reposted')

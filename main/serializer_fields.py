# Rest framework
from rest_framework import serializers

class CategoriesField(serializers.RelatedField):
    """ 
    Remove notes from the returned json
    """
    def to_representation(self, value):
        return {
                'id': value.id,
                'category': value.category,
                }

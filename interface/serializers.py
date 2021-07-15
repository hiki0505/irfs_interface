from rest_framework import serializers

from .models import DatabaseCredentials
from .services import db_connection
import psycopg2
import pyodbc
import pymysql
import cx_Oracle as co

# from .models import Irfs


# class Ifrs9Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = Irfs
#         fields = '__all__'


class DatabaseConnectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DatabaseCredentials
        fields = '__all__'
    # engine = serializers.CharField()
    # host = serializers.CharField()
    # username = serializers.CharField()
    # password = serializers.CharField()
    # dbname = serializers.CharField()

    def validate(self, data):
        # engine = data['engine']
        # host = data['host']
        # username = data['username']
        # password = data['password']
        # dbname = data['dbname']
        try:
            conn = db_connection(**data)
        except (pymysql.OperationalError, pyodbc.OperationalError, psycopg2.OperationalError, co.OperationalError):
            raise serializers.ValidationError("FATAL ERROR: Authentication failed for user {}".format(data['username']))
        if conn is None:
            raise serializers.ValidationError("Invalid credentials of your database!")
        DatabaseCredentials.objects.create(**data)
        return data
from datetime import date

from django.core.validators import int_list_validator, validate_comma_separated_integer_list
from django.db import models

# class PList(models.Model):
#     prod_id = models.CommaSeparatedIntegerField


class DatabaseCredentials(models.Model):
    ENGINE_CHOICES = (
        ('postgres', 'postgres'),
        ('pymysql', 'pymysql'),
        ('pyodbc', 'pyodbc'),
        ('oracle', 'oracle')
    )
    engine = models.CharField(default='postgres', max_length=50, choices=ENGINE_CHOICES)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    dbname = models.CharField(max_length=255)


class Ifrs(models.Model):
    repd_start = models.DateField(null=True, blank=True)
    repd_end = models.DateField(null=True, blank=True)
    PERIOD_CHOICES = (
        ('monthly', 'monthly'),
        ('yearly', 'yearly')
    )
    repd_period = models.CharField(max_length=50, choices=PERIOD_CHOICES, null=True, blank=True)

    repd = models.CharField(max_length=255)
    resd = models.CharField(max_length=255)
    st_date = models.CharField(max_length=255)
    end_date = models.CharField(max_length=255)
    bthday = models.CharField(max_length=255)

    dp = models.CharField(max_length=255)
    di = models.CharField(max_length=255)

    anp_m = models.CharField(max_length=255)
    anp_c = models.CharField(max_length=255)
    aop_m = models.CharField(max_length=255)
    aop_c = models.CharField(max_length=255)

    ani_m = models.CharField(max_length=255)
    ani_c = models.CharField(max_length=255)
    aoi_m = models.CharField(max_length=255)
    aoi_c = models.CharField(max_length=255)

    # total_outstanding = ?
    aor_m = models.CharField(max_length=255)
    aor_c = models.CharField(max_length=255)

    int_rate = models.CharField(max_length=255)

    id_l = models.CharField(max_length=255)
    id_c = models.CharField(max_length=255)
    id_sub = models.CharField(max_length=255)


    # bid = "debt_standard_gl_acct_no" # balance account No
    cid = models.CharField(max_length=255)
    pid = models.CharField(max_length=255)
    ctype = models.CharField(max_length=255)
    ptype = models.CharField(max_length=255)
    # plist = models.CharField(max_length=255, null=True, blank=True)
    # plist_cons = models.CharField(max_length=255, null=True, blank=True)
    # plist_corp = models.CharField(max_length=255, null=True, blank=True)
    # plist_sole = models.CharField(max_length=255, null=True, blank=True)
    wrof = models.CharField(max_length=255)


# class Plist(models.Model):
#     name = models.CharField(max_length=255)
#     product_code = models.CharField(max_length=255)
    # class Meta:
    #     db_table = "MF"

    # STATUS_CHOICES = (
    #     (7, 'Low'),
    #     (12, 'Normal'),
    #     (13, 'High'),
    # )
    #  plist =
    # wrof =

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


# class Irfs(models.Model):
#     DATE_OPER = models.DateTimeField(verbose_name='repd', help_text='report date for the portfolio')
#     REST_NEW = models.DateTimeField(verbose_name='resd', help_text='date of restructuring')
#     DATE_OPEN = models.DateTimeField(verbose_name='st_date', help_text='loan origination date')
#     DATE_PLANCLOSE = models.DateTimeField(verbose_name='end_date', help_text='contractual loan maturity date')
#     DATEOFBIRTH = models.DateTimeField(verbose_name='bthday', help_text='date of birth')
#
#     OVERDUEDAY = models.IntegerField(verbose_name='dp', help_text='days principal is past due')
#     INTEREST_OVERDUEDAY = models.IntegerField(verbose_name='di', help_text='days interest is past due')
#
#     SUMMAAZN = models.DecimalField(verbose_name='anp_m', help_text='normal principal amount in manats',
#                                    max_digits=19,
#                                    decimal_places=10)
#     SUMMA = models.DecimalField(verbose_name='anp_c', help_text='normal principal amount in currency',
#                                 max_digits=19,
#                                 decimal_places=10
#                                 )
#     SUMMA_19AZN = models.DecimalField(verbose_name='aop_m', help_text='overdue principal amount in manats',
#                                       max_digits=19,
#                                       decimal_places=10
#                                       )
#     SUMMA_19 = models.DecimalField(verbose_name='aop_c', help_text='overdue principal amount in currency',
#                                    max_digits=19,
#                                    decimal_places=10
#                                    )
#
#     PROCAZN = models.DecimalField(verbose_name='ani_m', help_text='normal interest amount in manats',
#                                   max_digits=19,
#                                   decimal_places=10
#                                   )
#     PROC = models.DecimalField(verbose_name='ani_c', help_text='normal interest amount in currency',
#                                max_digits=19,
#                                decimal_places=10
#                                )
#     PROCPROSAZN = models.DecimalField(verbose_name='aoi_m', help_text='overdue interest amount in manats',
#                                       max_digits=19,
#                                       decimal_places=10
#                                       )
#     PROCPROS = models.DecimalField(verbose_name='aoi_c', help_text='overdue interest amount in currency',
#                                    max_digits=19,
#                                    decimal_places=10
#                                    )
#
#     # total_outstanding = ?
#     SUMMAKREAZN = models.DecimalField(verbose_name='aor_m', help_text='original amount in manats',
#                                       max_digits=19,
#                                       decimal_places=10
#                                       )
#     SUMMAKRE = models.DecimalField(verbose_name='aor_c', help_text='original amount in currency',
#                                    max_digits=19,
#                                    decimal_places=10
#                                    )
#
#     PROCSTAVKRE = models.DecimalField(verbose_name='int_rate', help_text='Interest rate',
#                                       max_digits=19,
#                                       decimal_places=10
#                                       )
#
#     KOD1 = models.IntegerField(verbose_name='id_l', help_text='contract (loan) ID if any')
#     LICSCHKRE = models.IntegerField(verbose_name='id_c', help_text='client ID')
#     id_sub = models.IntegerField(help_text='subaccount (order of loan)')
#
#     # bid = "debt_standard_gl_acct_no" # balance account No
#     cid = models.IntegerField(verbose_name='KODVALUTI', help_text='currency ID (or name)')
#     pid = models.IntegerField(verbose_name='TIPKREDITA', help_text='product ID or name')
#
#     plist = models.CharField(validators=[validate_comma_separated_integer_list], max_length=50)
#     wrof = models.IntegerField(verbose_name='WROF', help_text='write-off status column')
#
#     class Meta:
#         db_table = "MF"

    # STATUS_CHOICES = (
    #     (7, 'Low'),
    #     (12, 'Normal'),
    #     (13, 'High'),
    # )
    #  plist =
    # wrof =

from django.core.validators import int_list_validator, validate_comma_separated_integer_list
from django.db import models

# class PList(models.Model):
#     prod_id = models.CommaSeparatedIntegerField

class Irfs(models.Model):
    repd = models.DateTimeField(verbose_name='DATE_OPER', help_text='report date for the portfolio')
    resd = models.DateTimeField(verbose_name='REST_NEW', help_text='date of restructuring')
    st_date = models.DateTimeField(verbose_name='DATE_OPEN', help_text='loan origination date')
    end_date = models.DateTimeField(verbose_name='DATE_PLANCLOSE', help_text='contractual loan maturity date')
    bthday = models.DateTimeField(verbose_name='DATEOFBIRTH', help_text='date of birth')

    dp = models.IntegerField(verbose_name='OVERDUEDAY', help_text='days principal is past due')
    di = models.IntegerField(verbose_name='INTEREST_OVERDUEDAY', help_text='days interest is past due')

    anp_m = models.DecimalField(verbose_name='SUMMAAZN', help_text='normal principal amount in manats',
                                max_digits=19,
                                decimal_places=10)
    anp_c = models.DecimalField(verbose_name='SUMMA', help_text='normal principal amount in currency',
                                max_digits=19,
                                decimal_places=10
                                )
    aop_m = models.DecimalField(verbose_name='SUMMA_19AZN', help_text='overdue principal amount in manats',
                                max_digits=19,
                                decimal_places=10
                                )
    aop_c = models.DecimalField(verbose_name='SUMMA_19', help_text='overdue principal amount in currency',
                                max_digits=19,
                                decimal_places=10
                                )

    ani_m = models.DecimalField(verbose_name='PROCAZN', help_text='normal interest amount in manats',
                                max_digits=19,
                                decimal_places=10
                                )
    ani_c = models.DecimalField(verbose_name='PROC', help_text='normal interest amount in currency',
                                max_digits=19,
                                decimal_places=10
                                )
    aoi_m = models.DecimalField(verbose_name='PROCPROSAZN', help_text='overdue interest amount in manats',
                                max_digits=19,
                                decimal_places=10
                                )
    aoi_c = models.DecimalField(verbose_name='PROCPROS', help_text='overdue interest amount in currency',
                                max_digits=19,
                                decimal_places=10
                                )

    # total_outstanding = ?
    aor_m = models.DecimalField(verbose_name='SUMMAKREAZN', help_text='original amount in manats',
                                max_digits=19,
                                decimal_places=10
                                )
    aor_c = models.DecimalField(verbose_name='SUMMAKRE', help_text='original amount in currency',
                                max_digits=19,
                                decimal_places=10
                                )

    int_rate = models.DecimalField(verbose_name='PROCSTAVKRE', help_text='Interest rate',
                                   max_digits=19,
                                   decimal_places=10
                                   )

    id_l = models.IntegerField(verbose_name='KOD1', help_text='contract (loan) ID if any')
    id_c = models.IntegerField(verbose_name='LICSCHKRE', help_text='client ID')
    id_sub = models.IntegerField(help_text='subaccount (order of loan)')


    # bid = "debt_standard_gl_acct_no" # balance account No
    cid = models.IntegerField(verbose_name='KODVALUTI', help_text='currency ID (or name)')
    pid = models.IntegerField(verbose_name='TIPKREDITA', help_text='product ID or name')

    plist = models.CharField(validators=[validate_comma_separated_integer_list], max_length=50)
    wrof = models.IntegerField(verbose_name='WROF', help_text='write-off status column')

    class Meta:
        db_table = "MF"

    # STATUS_CHOICES = (
    #     (7, 'Low'),
    #     (12, 'Normal'),
    #     (13, 'High'),
    # )
    #  plist =
    # wrof =

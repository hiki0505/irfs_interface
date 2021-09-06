p0 = "select * from "

stg1 = ""
stg2 = ""

for i in range(0, 10):
    x1 = """union (select t0.{repd}, count(t0.acc) as orig_count, 
    sum(t0.amt) as orig_amount, sum(nvl(t3.deft,0))/count(t0.acc) as rate from """.format(repd='repd')

    stg1 += x1

    x2 = """(select max({repd}) as {repd}, {id_c} as acc, sum(({anp_m}+{aop_m})) as amt, 
    case 
    when (max(greatest(nvl({dp},0), nvl({di},0))) > 90) or 
    ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) 
    and nvl(max({repd})-max({resd}),999) < 182) then 'stage3'
    when ((max(greatest(nvl({dp},0), nvl({di},0))) between 31 and 90) and 
    (nvl(max({repd})-max({resd}),999) > 181)) or 
    ((max(greatest(nvl({dp},0), nvl({di},0))) between 11 and 30) and 
    nvl(max({repd})-max({resd}),999) < 182) then 'stage2' 
    else 'stage1' end as par_status 
    from {dbt} where {repd} = '{start}' and 
    {pid} in {plist} and {ptype}='A' group by {id_c}) t0""".format(repd='12/31/2017', resd='12/31/2017',
                                                                   id_c='1', anp_m='2', aop_m='3', dp='vafli',
                                                                   di='di', dbt='dbt', start='12/31/2017', pid='pidka',
                                                                   plist='plist', ptype='ptype')

    stg1 += x2

    past6_stage = """ left outer join (select {id_c} as acc1, 
        case 
        when max(greatest(nvl({dp},0), nvl({di},0)))>90 or 
        max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and  
        nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 3 
        when 
        max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and 
        nvl({repd}-{resd},999) > 181 then 1 else 0 end) = 1 or 
        max(case when (greatest(nvl({dp},0), nvl({di},0)) between 11 and 30) and 
        nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 2 
        else 1 end as past6_stage      
        from {dbt} where {repd} < '{i}' and {repd} > '{stage2_st_date}' group by {id_c}) 
        t1 on t0.acc = t1.acc1 """.format(
        dbt='dbt', i=i, stage2_st_date='stage2_st_date', repd='repd', resd='resd', id_c='id_c', dp='dp', di='di')

    stg1 += past6_stage

    past7_12_stage = """ left outer join (select {id_c} as acc2, 
        case 
        when max(greatest(nvl({dp},0), nvl({di},0)))>90 or 
        max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and  
        nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 3 
        when 
        max(case when (greatest(nvl({dp},0), nvl({di},0)) between 31 and 90) and 
        nvl({repd}-{resd},999) > 181 then 1 else 0 end) = 1 or 
        max(case when (greatest(nvl({dp},0), nvl({di},0)) between 11 and 30) and 
        nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1 then 2 
        else 1 end as past712_stage       
        from {dbt} where {repd} < '{stage2_st_date}' and {repd} > '{stage3_st_date}' group by {id_c}) 
        t2 on t0.acc = t2.acc2 """.format(
        dbt='dbt', stage2_st_date='stage2_st_date', stage3_st_date='stage3_st_date', repd='repd',
        resd='resd', id_c='id_c', dp='dp', di='di')

    stg1 += past7_12_stage

    x3 = """
    left outer join 
    (select {id_c} as acc3, 
    case 
    when max(greatest(nvl({dp},0), nvl({di},0)))>90 or 
    max(case when (greatest(nvl({dp},0), nvl({di},0)) between 11 and 30) and  
    nvl({repd}-{resd},999) < 182 then 1 else 0 end) = 1
    then 1 else 0 end as deft from {dbt} where {repd} > '{start}' and {repd} < '{end}'
    group by {id_c}) t3 on t0.acc = t3.acc3
    """.format(dbt='dbt', repd='repd', resd='resd', id_c='id_c', anp_m='anp_m', aop_m='aop_m',
               dp='dp', di='di', start=i, end='end_date')

    stg1 += x3

    stg1 += " where t0.par_status='stage1' and nvl(t1.past6_stage,1)=1 and nvl(t2.past712_stage,1)!=3 group by t0.{repd}) ".format(
        repd='repd')

print(stg1)
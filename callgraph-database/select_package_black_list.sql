with packages (package_name, sum_quantity) as (
    with repeated_edges (caller, caller_package, callee, callee_package, quantity) as (
        select caller, caller_package, callee, callee_package, count(*)
        from edges
        group by caller, caller_package, callee, callee_package
        having count(*) > 10
    )
    select caller_package, sum(quantity) from repeated_edges group by caller_package
    union
    select callee_package, sum(quantity) from repeated_edges group by callee_package
)
select package_name, sum(sum_quantity) from packages group by package_name;

-- edge black list
select caller, callee, 'M:' || caller || ' (O)' || callee, count(*)
from edges
group by caller, callee, 'M:' || caller || ' (O)' || callee
--order by count(*) desc
having count(*) > 20;

with apps (app) as (select app from edges group by app)
select count(*) from apps;
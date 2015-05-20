-- APK INFORMATION

-- number of apps by rating
select count(*) from apkinformation where cast(userrating as FLOAT) < 4.0;
select count(*) from apkinformation where cast(userrating as FLOAT) >= 4.0;

-- apps grouped by lowerdownloads
select lowerdownloads, count(*), avg(numberofreviews) from apkinformation
group by lowerdownloads
order by lowerdownloads;

-- apps grouped by userrating + histogram
select userrating, count(*), avg(numberofreviews), RPAD('#', CAST(count(*) / 40 AS int), '#') 
from apkinformation
group by userrating
order by userrating;

-- REVIEWS

-- testing full text search
with distinct_reviews as (
  SELECT app_id, title, body, count(*) FROM reviews
  --where rating = ' Rated 5 stars out of five stars '
  GROUP BY app_id, title, body
  order by app_id
)
select to_tsvector(title), 
       to_tsvector(body), 
       to_tsvector(title) @@ to_tsquery('scam') as title_match,
       to_tsvector(body) @@ to_tsquery('scam') as body_match
from distinct_reviews
where to_tsvector(title) @@ to_tsquery('scam') = true
   or to_tsvector(body) @@ to_tsquery('scam') = true;

select to_tsvector('Unsafe Glitch asda aqweq Rooted'), 
  to_tsvector('Unsafe Glitch asda aqweq Rooted') @@ to_tsquery('unsafe | glitch');

-- get reviews by rating
SELECT app_id, title, body, count(*) FROM reviews
where rating = ' Rated 1 stars out of five stars '
GROUP BY app_id, title, body
order by app_id;

-- get all different ratings
select rating from reviews group by rating;

-- number of unique reviews
with distinct_reviews as (
    SELECT app_id, title, body, rating, count(*) FROM reviews
    --where app_id = 'com.smartPhones.clockwidget.ncaa.live.georgia_AND'
    GROUP BY app_id, title, body, rating
)
select count(*) from distinct_reviews;

-- Number of usable reviews
with distinct_reviews as (
    SELECT app_id, title, body, count(*) FROM reviews
    GROUP BY app_id, title, body
)
select count(*) 
from apkinformation as a 
inner join distinct_reviews as r on a.apkname = r.app_id
where a.isjavaanalyze = true and a.isreviewsdownloaded = true;


-- Number of apps with usable reviews
with apps as (
  with distinct_reviews as (
      SELECT app_id, title, body, count(*) FROM reviews
      GROUP BY app_id, title, body
  )
  select app_id, count(*)
  from distinct_reviews group by app_id
)
select count(*) from apps;






-- ATTACK SURFACE

-- black list edge collapse performance
select apk_name, 
  original_node_count, 
  collapsed_node_count, 
  original_node_count - collapsed_node_count as diff 
from collapse_data;

-- edge black list as a java-callgraph
select caller, callee, 'M:' || caller || ' (O)' || callee, count(*)
from black_listed_edges
group by caller, callee, 'M:' || caller || ' (O)' || callee
having count(*) >= 25
order by count(*) desc;

-- number of times each edge appears
with edges_count (caller, callee, number_of_appearances_in_apps) as 
(
  select caller, callee, count(*)
  from black_listed_edges
  group by caller, callee
  having count(*) >= 10
)
select 'M:' || caller || ' (O)' || callee as entry, number_of_appearances_in_apps
from edges_count
order by caller, callee;

-- distribution of edges by the number of apps in which they appear
with q (fa,fb, number_of_apps_appeared) as 
(
  select caller, callee, count(*)
  from black_listed_edges
  group by caller, callee
  --having count(*) > 23
)
select number_of_apps_appeared, count(*), RPAD('#', CAST((count(*) / 50) as int), '#')
from q 
group by number_of_apps_appeared
order by number_of_apps_appeared;

select avg(entry_points_count) from attack_surfaces;
select avg(exit_points_count) from attack_surfaces;



-- WORK QUERIES

-- Master data query. Every app with its metrics and reviews with security word count.
--with q as (
WITH app_reviews_security_words AS (
    WITH words_in_reviews AS (
        WITH distinct_reviews AS (
            SELECT
              app_id,
              title,
              body,
              count(*)
            FROM reviews
            GROUP BY app_id, title, body
        )
        SELECT
          app_id,
          to_tsvector(title) @@ to_tsquery(
              'unsafe | glitch | rooted | permission | unlock | crash | scam | privacy | risk | pop') AS title_match,
          to_tsvector(body) @@ to_tsquery(
              'unsafe | glitch | rooted | permission | unlock | crash | scam | privacy | risk | pop') AS body_match
        FROM distinct_reviews
        ORDER BY app_id
    )
    SELECT
      app_id,
      SUM(CAST(title_match AS INTEGER))                                    AS titles_with_security_words,
      SUM(CAST(body_match AS INTEGER))                                     AS bodies_with_security_words,
      SUM(CAST(title_match AS INTEGER)) + SUM(CAST(body_match AS INTEGER)) AS reviews_with_security_words
    FROM words_in_reviews
    GROUP BY app_id
)
SELECT
  arsw.*,
  apkinfo.*,
  atksrf.* --, 
--        (select AVG(n.entry_page_rank)
--         from nodes as n
--         where n.attack_surface_id = atksrf.id 
--           and n.is_entry_point = true) as average_entry_page_rank_of_entry_points,
--        (select AVG(n.exit_page_rank)
--         from nodes as n
--         where n.attack_surface_id = atksrf.id
--           and n.is_exit_point = true) as average_exit_page_rank_of_exit_points
FROM app_reviews_security_words AS arsw
  INNER JOIN apkinformation AS apkinfo ON arsw.app_id = apkinfo.apkname
  INNER JOIN attack_surfaces AS atksrf ON arsw.app_id = atksrf.source;
--)
--select count(*) from q;


-- callgraph measurement and reviews progress
select
  (select count(*) from apkinformation where isjavaanalyze = true and isreviewsdownloaded = true) as ready,
  (select count(*) from apkinformation where isjavaanalyze = true) as analyzed,
  (select count(*) from apkinformation where isreviewsdownloaded = true) as reviewsdownloaded;

select count(*) from apkinformation where isdownloaded = TRUE;
select count(*) from reviews;

/*
3459, 3468, 5963
3491, 3497, 6043
3608,3609,6239

3994,4031,7267
4021,4032,7314

4037,4040,7441
*/


select title, rating, body, count(*) from reviews where app_id = 'com.oasisfeng.greenify' GROUP BY title, rating, body;


select count(*)
from apkinformation as a 
left outer join reviews as r on a.apkname = r.app_id
where r.app_id is NULL and a.isjavaanalyze = TRUE and a.isreviewsdownloaded = TRUE;


select count(*) from apkinformation where isjavaanalyze = true and isreviewsdownloaded = true;

select count(*) from black_listed_edges_all_apps;



-- DISTRIBUTION OF INPUT METHODS

select method_package, (CAST(count(*) as FLOAT ) / 364) * 100 as percent
from input_methods
group by method_package
order by percent desc;

select method_package, (CAST(count(*) as FLOAT ) / 364) * 100 as percent
from input_methods 
group by method_package 
having (CAST(count(*) as FLOAT ) / 364) * 100 >= 1;

with q as (
  select method_package, (CAST(count(*) as FLOAT ) / 364) * 100 as percent
  from input_methods
  group by method_package
  having (CAST(count(*) as FLOAT ) / 364) * 100 < 1
)
select SUM(percent) from q;




select * from output_methods;

select method_package, (CAST(count(*) as FLOAT ) / 304) * 100 as percent
from output_methods
group by method_package
order by percent desc;

select method_package, (CAST(count(*) as FLOAT ) / 304) * 100 as percent
from output_methods
group by method_package
having (CAST(count(*) as FLOAT ) / 304) * 100 >= 1;

with q as (
    select method_package, (CAST(count(*) as FLOAT ) / 304) * 100 as percent
    from output_methods
    group by method_package
    having (CAST(count(*) as FLOAT ) / 304) * 100 < 1
)
select SUM(percent) from q;

-- other = 10.855263157894735

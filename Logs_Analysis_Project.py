#!/usr/bin/env python3
#
# This is the submission of Logs Analysis Project

import psycopg2

db = psycopg2.connect("dbname=vagrant")
cursor = db.cursor()

articleQuery = """SELECT a.title, count(*) visited
                    FROM log l, articles a
                    WHERE l.path like '%article%'
                        AND l.status = '200 OK'
                        AND SUBSTRING(l.path,10) = a.slug
                    GROUP BY a.title
                    ORDER BY visited DESC
                    LIMIT 3;"""

print("\n========== most popular three articles of all time ==========\n")
cursor.execute(articleQuery)
rows = cursor.fetchall()

for row in rows:
    current = "%s - %s Views" % (row[0], row[1])
    print(current)

authorQuery = """SELECT Name, SUM(visited) Total
                    FROM (
                        SELECT ar.id, at.name ,
                            SUBSTRING(path,10) article, count(*) visited
                        FROM log, articles ar, authors at
                        WHERE path like '%article%'
                            AND status = '200 OK'
                            AND SUBSTRING(path,10) = ar.slug
                            AND ar.author = at.id
                            GROUP BY ar.id, path, at.name
                            ORDER BY visited desc) AS temp
                        GROUP BY Name
                        ORDER BY Total DESC;"""

print("\n========= most popular article authors of all time =========\n")
cursor.execute(authorQuery)
rows = cursor.fetchall()

for row in rows:
    current = "%s - %s Views" % (row[0], row[1])
    print(current)


errorQuery = """SELECT COUNT(l.status) errors, temp.statusall all_status,
                    ROUND(((COUNT(l.status)::decimal / temp.statusall)
                        * 100), 2) percentage,
                    to_char(l.time, 'Month DD, YYYY') date
                    FROM log l,
                        (SELECT COUNT(ll.status) statusall,
                            to_char(ll.time, 'Month DD, YYYY') date
                        FROM log ll
                        GROUP BY to_char(ll.time, 'Month DD, YYYY')
                        ORDER BY to_char(ll.time, 'Month DD, YYYY')) temp
                    WHERE l.status = '404 NOT FOUND'
                        AND date(l.time) = date(temp.date)
                    GROUP BY to_char(l.time, 'Month DD, YYYY'), temp.statusall
                    ORDER BY percentage desc;"""

print("\n===== days have more than 1% of requests lead to errors =====\n")
cursor.execute(errorQuery)
rows = cursor.fetchall()

for row in rows:
    if row[2] > 1:
        current = "%s - %s %% errors" % (row[3], row[2])
        print(current)

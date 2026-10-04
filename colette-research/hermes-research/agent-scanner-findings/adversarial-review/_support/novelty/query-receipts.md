# Public read-only query receipts

Generated from feed-tests.jsonl and archive-tests.jsonl. No source response bodies are stored.

## urlscan-june-google
URL: https://urlscan.io/api/v1/search/?q=domain%3Agoogle.com+AND+date%3A%5B2026-06-18+TO+2026-06-19%5D&size=3
Retrieved UTC: 2026-10-04T01:14:04.040130+00:00

Query domain:google.com AND date:[2026-06-18 TO 2026-06-19]; HTTP 200; total 0; has_more False.

## urlscan-recent-sec
URL: https://urlscan.io/api/v1/search/?q=task.domain%3Asec.gov+AND+date%3A%5B2026-09-04+TO+2026-10-04%5D&size=10
Retrieved UTC: 2026-10-04T01:13:54.325939+00:00

Query task.domain:sec.gov AND date:[2026-09-04 TO 2026-10-04]; HTTP 200; total 60; has_more False.

## urlscan-june-sec
URL: https://urlscan.io/api/v1/search/?q=task.domain%3Asec.gov+AND+date%3A%5B2026-06-18+TO+2026-06-19%5D&size=10
Retrieved UTC: 2026-10-04T01:13:39.971084+00:00

Query task.domain:sec.gov AND date:[2026-06-18 TO 2026-06-19]; HTTP 200; total 0; has_more False.

## greynoise-401
URL: https://api.greynoise.io/v2/experimental/gnql?query=raw_data.http.path%3A%22%2Acounty.json%2A%22&size=1
Retrieved UTC: 2026-10-04T01:17:17.359969+00:00

Query raw_data.http.path:"*county.json*"; HTTP 401; response message unauthorized.

## wayback-aihw
URL: https://web.archive.org/cdx/search/cdx?url=r.jina.ai%2Fhttp%3A%2F%2Fhttps%3A%2F%2Fwww.aihw.gov.au%2Fgetmedia%2F57e4c61f%2A&from=20260618&to=20260618&output=json&fl=timestamp%2Curlkey%2Cstatuscode&limit=10
Retrieved UTC: 2026-10-04T01:23:10.071590+00:00

CDX result for wayback-aihw; HTTP 200; records [["20260618063135", "ai,jina,r)/http:/https:/www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/principal-diagnosis-cube_2014-15.xlsx.aspx", "200"]].

## wayback-county
URL: https://web.archive.org/cdx/search/cdx?url=sec.gov%2Ffiles%2Fcounty.json&matchType=prefix&from=20260618&to=20260618&output=json&fl=timestamp%2Curlkey%2Coriginal%2Cdigest%2Cstatuscode&limit=200
Retrieved UTC: 2026-10-04T01:23:33.930066+00:00

CDX result for wayback-county; HTTP 200; count 63; first ['20260618022300', '20260618022326', '20260618065925', '20260618141937', '20260618143938', '20260618143941'].

## wayback-report-sep24
URL: https://web.archive.org/cdx/search/cdx?url=transluce.org%2Fagent-activity&from=20260901&to=20261003&output=json&fl=timestamp%2Coriginal%2Cstatuscode&filter=statuscode%3A200&collapse=timestamp%3A8&limit=30
Retrieved UTC: 2026-10-04T01:20:06.986896+00:00

CDX result for wayback-report-sep24; HTTP 200; count 6; first [['20260924031053', 'https://transluce.org/agent-activity', '200'], ['20260925021236', 'https://transluce.org/agent-activity', '200'], ['20260926113612', 'https://transluce.org/agent-activity', '200'], ['20260927040012', 'https://transluce.org/agent-activity', '200'], ['20261001134622', 'https://transluce.org/agent-activity', '200'], ['20261002121956', 'https://transluce.org/agent-activity', '200']].


## urlquery-api-401
URL: https://api.urlquery.net/public/v1/search/reports/?query=http.url.addr%3A%2Acounty.json%2A+AND+date%3A%5B2026-06-18+TO+2026-06-19%5D

Public read-only lookup urlquery-api-401; HTTP 401; retrieved 2026-10-04T01:15:08.486224+00:00.

## urlscan-result-403
URL: https://urlscan.io/api/v1/result/019ed827-0471-746c-aa31-8da7d1e6f6ae/

Public read-only lookup urlscan-result-403; HTTP 403; retrieved 2026-10-04T01:21:42.506071+00:00.

## urlscan-public-429
URL: https://urlscan.io/result/019ed827-0471-746c-aa31-8da7d1e6f6ae/

Public read-only lookup urlscan-public-429; HTTP 429; retrieved 2026-10-04T01:21:50.935859+00:00.

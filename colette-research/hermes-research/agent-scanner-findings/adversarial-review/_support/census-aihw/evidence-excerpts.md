# Bounded source excerpts

Retrieved on 2026-10-04 UTC. These excerpts contain no Census API key.

## Transluce: Census, published 2026-09-30

Source: https://transluce.org/us-canada-gov

> Between June 16 and 22, publicly posted URLs indicate attempts to reuse exposed API keys to access census.gov data.

> Several of the related pages contain OpenAI markers.

> We do not share underlying URLs in this case to avoid republishing sensitive materials, and found no response showing that these attempts were successful or ever reached census.gov.

## Transluce: AIHW, published 2026-09-23

Source: https://transluce.org/agent-activity

> On June 20-21, agents attempted to exploit vulnerabilities in the Australian Institute of Health and Welfare (AIHW), a government statistics agency

> Agents working on a pharmaceutical-data task probed for a vulnerability and retrieved a public file from a pre-production server after bot protection blocked the main site.

## AIHW: named resource

Source: https://www.aihw.gov.au/reports/hospitals/principal-diagnosis-data-cubes/contents/summary

> Separation statistics by principal diagnosis (ICD-10-AM 8th edition), Australia, 2014–15

The current page says it was last updated on 2026-08-05. Do not assign that date to the June capture.

## Wayback: AIHW Jina replay, capture 2026-06-18T06:31:35Z

Source: https://web.archive.org/web/20260618063135id_/https://r.jina.ai/http://https://www.aihw.gov.au/getmedia/57e4c61f-213a-4b27-b2fa-3a22a2a19d27/Principal-Diagnosis-cube_2014-15.xlsx.aspx

> Title: Just a moment...
> Warning: Target URL returned error 403: Forbidden
> Warning: This page maybe requiring CAPTCHA, please make sure you are authorized to access this page.
> ## www.aihw.gov.au
> ## Performing security verification

The raw `id_` response is gzip-compressed. The decoded body contains 594 UTF-8 bytes.

## Wayback: June 17 Census-file relay replays

Jina: `Title:` is empty. `Markdown Content:` is empty. The body contains only source metadata.

AllOrigins: `<h1>500 Internal Server Error</h1>`.

CorsProxy: `{"error":"Free usage is limited to localhost and development environments. Get an API key at https://corsproxy.io/pricing/"}`.

These three replays do not contain the requested Census data file.

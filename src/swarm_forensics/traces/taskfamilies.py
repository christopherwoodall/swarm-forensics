"""Task-family classification for arquivo capture targets.

A task family is visible request structure: the destination host plus a
coarse path/parameter template. It is NOT a mechanism claim and NOT an
attribution. Two rows in the same task family show the same kind of work was
attempted; nothing more.

Templates are derived from the us-canada evidence package's own target set
(15 government data families). Unknown hosts fall back to a host-only label.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

# (host substring, path/param template regex, family label)
TEMPLATES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "civilrightsdata.ed.gov",
        re.compile(r"/api/v1\.0/GetStateEstimation"),
        "crdc_state_estimation",
    ),
    (
        "civilrightsdata.ed.gov",
        re.compile(r"/api/v1\.0/GetNationalEstimation"),
        "crdc_national_estimation",
    ),
    (
        "civilrightsdata.ed.gov",
        re.compile(r"/api/v1\.0/GetStateNationalEstimation"),
        "crdc_state_national_estimation",
    ),
    (
        "civilrightsdata.ed.gov",
        re.compile(r"/api/v1\.0/SurveyYearsList"),
        "crdc_survey_years",
    ),
    (
        "reportcard.msde.maryland.gov",
        re.compile(r"/DataDownloads/2022/2022/"),
        "md_reportcard_2022_download",
    ),
    (
        "reportcard.msde.maryland.gov",
        re.compile(r"/DataDownloads/2023/2022/"),
        "md_reportcard_2023_2022_download",
    ),
    (
        "reportcard.msde.maryland.gov",
        re.compile(r"/DataDownloads/2023/2023/"),
        "md_reportcard_2023_2023_download",
    ),
    (
        "reportcard.msde.maryland.gov",
        re.compile(r"/DataDownloads/FileDownload"),
        "md_reportcard_file_download",
    ),
    (
        "reportcard.msde.maryland.gov",
        re.compile(r"/DataDownloads/202[23]/MCA[Pp]"),
        "md_mcap_download",
    ),
    (
        "reportcard.msde.maryland.gov",
        re.compile(r"/Assessments/Get"),
        "md_assessment_api",
    ),
    (
        "msp2018.msde.maryland.gov",
        re.compile(r""),
        "md_msp2018",
    ),
    (
        "kansasmemory.gov",
        re.compile(r""),
        "kansas_memory",
    ),
    (
        "history.navy.mil",
        re.compile(r""),
        "navy_history",
    ),
    (
        "apps.bea.gov",
        re.compile(r""),
        "bea_api",
    ),
    (
        "bac-lac.canada.ca",
        re.compile(r""),
        "canada_lac_search",
    ),
    (
        "data.nysed.gov",
        re.compile(r""),
        "nysed_enrollment",
    ),
    (
        "iquery.illinois.gov",
        re.compile(r""),
        "illinois_iquery",
    ),
    (
        "login.max.gov",
        re.compile(r""),
        "max_gov_budget",
    ),
    (
        "sec.gov",
        re.compile(r""),
        "sec_data",
    ),
)

_HOST_FALLBACK = re.compile(r"^[a-z0-9.-]+")


def task_family_for(target_url: str) -> str:
    """Return the coarse task-family label for one target URL."""
    if not target_url:
        return "unattributed_target"
    try:
        parts = urlsplit(target_url)
    except ValueError:
        return "unattributed_target"
    host = (parts.netloc or parts.path.split("/")[0] or "").lower()
    path = parts.path or ""
    for host_needle, pattern, label in TEMPLATES:
        if host_needle in host and pattern.search(path):
            return label
    if host:
        # host-only fallback; keeps the family honest about coverage
        slug = _HOST_FALLBACK.match(host.replace(":", "-"))
        return f"host:{slug.group(0)}" if slug else f"host:{host[:40]}"
    return "unattributed_target"

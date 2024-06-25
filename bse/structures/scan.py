import gql
from cachetools.func import ttl_cache
from gql import dsl

from bse.structures.bseidobject import BseIdObject
from bse.structures.site import Site
from bse.utils import RecrNameSpace


class ScanNotImplemented:
    @property
    def scan_target(self):
        # TODO: Test this query to understand exactly what it returns
        raise NotImplementedError

    @property
    def start_time(self):
        raise NotImplementedError

    @property
    def end_time(self):
        raise NotImplementedError

    @property
    def duration_in_seconds(self):
        raise NotImplementedError

    @property
    def status(self):
        raise NotImplementedError

    @property
    def agent(self):
        raise NotImplementedError

    @property
    def scan_metrics(self):
        raise NotImplementedError

    @property
    def scan_failure_code(self):
        raise NotImplementedError

    @property
    def scan_failure_message(self):
        raise NotImplementedError

    @property
    def scan_failure_cause(self):
        raise NotImplementedError

    @property
    def scan_failure_remedy(self):
        raise NotImplementedError

    @property
    def generated_by(self):
        raise NotImplementedError

    @property
    def scanner_version(self):
        raise NotImplementedError

    @property
    def scan_build_number(self):
        raise NotImplementedError

    @property
    def scan_configurations(self):
        raise NotImplementedError

    @property
    def extensions(self):
        raise NotImplementedError

    @property
    def scan_delta(self):
        raise NotImplementedError

    @property
    def jira_ticket_count(self):
        raise NotImplementedError

    @property
    def gitlab_issue_count(self):
        raise NotImplementedError

    @property
    def trello_card_count(self):
        raise NotImplementedError

    @property
    def issue_type_groups(self):
        raise NotImplementedError

    @property
    def issue_counts(self):
        raise NotImplementedError

    @property
    def audit_items(self):
        raise NotImplementedError

    @property
    def audit_item(self):
        raise NotImplementedError

    @property
    def scope(self):
        # This is actually scope_v2, I will not implement the deprecated scope query
        raise NotImplementedError

    @property
    def site_application_logins(self):
        raise NotImplementedError

    @property
    def schedule_item_application_logins(self):
        raise NotImplementedError

    @property
    def issues(self):
        raise NotImplementedError

    @property
    def warnings(self):
        raise NotImplementedError

    @property
    def settings(self):
        raise NotImplementedError


class ScanQueries:
    @ttl_cache(ttl=1)
    @staticmethod
    def template(scan_id: int, gql_connection: gql.Client) -> dict:
        query = None

        return gql_connection.execute(query)


class Scan(BseIdObject, ScanNotImplemented):
    pass

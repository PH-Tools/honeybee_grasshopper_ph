# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Airtable Download Table Data."""

import json

try:
    from typing import List, Any, Dict, TypeVar

    T = TypeVar("T")
except ImportError:
    pass  # IronPython 2.7

try:
    import System.Net  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class TableFields(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, str(k).upper(), v)

    def __repr__(self):
        return "AirtableFieldData({})".format(self.__dict__)

    def __str__(self):
        return self.__repr__()

    def ToString(self):
        return str(self)

    def get(self, k, _default=None):
        # type: (str, T) -> T
        return self.__dict__.get(str(k).upper(), _default)

    def __getitem__(self, key):
        return getattr(self, str(key).upper(), None)

    def items(self):
        return self.__dict__.items()


class TableRecord(object):
    def __init__(self, *args, **kwargs):
        self.ID = kwargs.get("id", "")
        self.CREATEDTIME = kwargs.get("createdTime", "")
        self.FIELDS = TableFields(**kwargs.get("fields", {}))

    def __repr__(self):
        return "AirtableDownloadTableData({})".format(self.__dict__)

    def __str__(self):
        return self.__repr__()

    def ToString(self):
        return str(self)


class GHCompo_AirTableDownloadTableData(object):
    """
    A class for downloading Airtable Data from a specific Base / Table
    """

    def __init__(self, _IGH, _token, _base_id, _table_id, _get_records, *args, **kwargs):
        # type: (gh_io.IGH, str, str, str, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.TOKEN = _token
        self.AIRTABLE_BASE_ID = _base_id
        self.AIRTABLE_TABLE_NAME = _table_id
        self.get_records = _get_records

    @property
    def ready(self):
        # type: () -> bool
        if not self.TOKEN:
            return False
        if not self.AIRTABLE_BASE_ID:
            return False
        if not self.AIRTABLE_TABLE_NAME:
            return False
        if not self.get_records:
            return False
        return True

    @property
    def url(self):
        # URL for the AirTable API
        _url = "https://api.airtable.com/v0/{}/{}".format(
            self.AIRTABLE_BASE_ID, self.AIRTABLE_TABLE_NAME
        )

        try:
            # TLS 1.2 is needed to download over https
            System.Net.ServicePointManager.SecurityProtocol = (
                System.Net.SecurityProtocolType.Tls12
            )
        except AttributeError:
            # TLS 1.2 is not provided by MacOS .NET in Rhino 5
            if _url.lower().startswith("https"):
                self.IGH.error(
                    "This system lacks the necessary security"
                    " libraries to download over https."
                )

        return _url

    def get_web_client(self, _offset="0"):
        # type: (str) -> System.Net.WebClient
        """Get a web client with Header and Query configuration for downloading data from AirTable."""

        if not self.TOKEN:
            raise ValueError("A token is required to download from AirTable.")

        client = System.Net.WebClient()
        client.Headers.Add("Authorization", "Bearer {}".format(self.TOKEN))
        client.Headers.Add("Content-type", "application/json")
        client.QueryString.Add("offset", _offset)

        return client

    def download_data(self):
        # type: (Any) -> List[Dict]
        """Download data from AirTable.

        Since AirTable limits the number of records that can be downloaded
        in a single request, this method will download all records in the table
        by making multiple requests using the 'offset' query parameter.
        """
        records = []
        offset = "0"

        while offset != None:
            client = self.get_web_client(offset)
            response = client.DownloadString(self.url)
            data = json.loads(response)
            records.extend(data.get("records", []))
            offset = data.get("offset", None)

        return records

    def run(self):
        # type: () -> List[TableRecord]
        """Run the component."""
        if not self.ready:
            return []

        try:
            response = self.download_data()
        except Exception as e:
            msg = "Failed to download file from AirTable.\n{}".format(e)
            self.IGH.warning(msg)
            return []

        return [TableRecord(**record) for record in response]

"""
This is a web scraper script using python to extract details of Microsoft 
Update Catalog for getting the relevant details of a windows update or patch.
With this script it is also possible to download the patch file to a location 

"""
import requests
import argparse
from bs4 import BeautifulSoup

BASE_SITE = "https://www.catalog.update.microsoft.com/ScopedViewInline.aspx"


def start():
    parser = argparse.ArgumentParser(
        description="This script is used for getting details about a patch or update from windows catalogue"
    )
    parser.add_argument(
        "-u",
        "--update-id",
        help="Enter the update id of the patch you want to get the details for",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--download",
        help="Add if patch file needed to be downloaded",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-p", "--path", help="Path to which patch file is to be downloaded"
    )
    parser.add_argument(
        "-file", "--file-name", help="Filename of the patch file to be downloaded"
    )
    args = parser.parse_args()
    return args


class Update:
    def __init__(self, update_id: str) -> None:
        self.update_id: str = update_id
        self.title: str = None
        self.description: str = None
        self.kb_number: str = None
        self.msrc_severity: str = None
        self.classification: str = None
        self.supported_products: str = None
        self.download_url: str = None
        self.get_update_details()
        self.get_update_download_link()

    def get_update_details(self):
        response = requests.get(BASE_SITE, params={"updateid": self.update_id})
        html_doc = response.content
        soup = BeautifulSoup(html_doc, "lxml")
        self.title = soup.find(
            "span", {"id": "ScopedViewHandler_titleText"}
        ).text.strip()
        self.description = soup.find(
            "span", {"id": "ScopedViewHandler_desc"}
        ).text.strip()
        self.kb_number = soup.find(
            "span", {"id": "ScopedViewHandler_labelKBArticle_Separator"}
        ).text.strip()
        self.msrc_severity = soup.find(
            "span", {"id": "ScopedViewHandler_msrcSeverity"}
        ).text.strip()
        self.classification = soup.find(
            "span", {"id": "ScopedViewHandler_labelClassification_Separator"}
        ).text.strip()
        self.supported_products = soup.find(
            "span", {"id": "ScopedViewHandler_labelSupportedProducts_Separator"}
        ).text.strip()

    def get_update_download_link(self):
        post_url = (
            'https://www.catalog.update.microsoft.com/DownloadDialog.aspx?updateIDs=[{"size":0,"languages":"","uidInfo":"'
            + self.update_id
            + '","updateID":"'
            + self.update_id
            + '"}]'
        )
        response = requests.post(post_url)
        html_doc = response.content
        soup = BeautifulSoup(html_doc, "lxml")
        script_string = soup.find_all("script")
        self.download_url = (
            script_string[1]
            .text.split("downloadInformation[0].files[0].url = '")[1]
            .split("';")[0]
        )


def download_update_file(download_url, download_path="", file_name=None):
    res = requests.get(download_url)
    if not file_name:
        file_name = download_url[download_url.rfind("/") + 1 :]
    if download_path:
        if not download_path[-1] == "/":
            download_path = download_path + "/"
    else:
        download_path = ""
    with open(download_path + file_name, "wb") as file:
        file.write(res.content)


if __name__ == "__main__":
    args = start()
    update_obj = Update(args.update_id)
    print(update_obj.__dict__)
    if args.download:
        download_update_file(update_obj.download_url, args.path, args.file_name)

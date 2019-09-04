# """
# Utilities for frosty to communicate with Google Sheets.
# """
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
#
#
# def get_sheet():
#     scope = ["https://spreadsheets.google.com/feeds",
#              "https://www.googleapis.com/auth/drive"]
#     creds = ServiceAccountCredentials.from_json_keyfile_name(
#         "client_secret.json",
#         scope
#     )
#     sheets_client = gspread.authorize(creds)
#     return sheets_client.open("ihscy finance sheet").sheet1
#
#

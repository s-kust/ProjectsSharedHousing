import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
# from IPython.core.debugger import set_trace
import os
import glob
import configparser
import asyncio
import datetime
import pandas as pd
import numpy as np
import mplfinance as mpf
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class DataStore:
    def __init__(self, config_input):
        self.config = config_input
        self.api_key = self.config["Alpha_vantage"]["api_key"]
        self.start_date = datetime.datetime.now() - datetime.timedelta(days=1.5 * 365)
        self.all_ideas = create_portfolio_df_from_worksheets()
        self.tickers_failed_import = []
        self.tickers_failed_processing = []
        self.all_tickers_data = {}
        self.last_api_call_time = self.subject = self.note = None


def atr(df, n=14):  # average true range
    data = df.copy()
    data["tr0"] = abs(data["High"] - data["Low"])
    data["tr1"] = abs(data["High"] - data["Close"].shift())
    data["tr2"] = abs(data["Low"] - data["Close"].shift())
    tr = data[["tr0", "tr1", "tr2"]].max(axis=1)
    atr_series = tr.ewm(alpha=1 / n, min_periods=n).mean()
    return atr_series


def create_email_subject(symbol1, symbol2=None):
    if symbol2 is None:
        email_subject = "Idea: " + symbol1
    else:
        email_subject = "Relative " + symbol1 + " " + symbol2
    return email_subject


def create_charts(tickers_data, symbol1, symbol2=None):
    folder = 'static'
    if symbol2 is None:
        job_type = "single"
        filename_1 = symbol1 + "_long_period" + ".png"
        filename_1 = os.path.join(folder, filename_1)
        filename_2 = symbol1 + "_short_period" + ".png"
        filename_2 = os.path.join(folder, filename_2)
        data = tickers_data[symbol1]
    else:
        job_type = "relative"
        filename_1 = symbol1 + "_" + symbol2 + ".png"
        filename_1 = os.path.join(folder, filename_1)
        filename_2 = None
        data = tickers_data[symbol1] / tickers_data[symbol2]
    my_plots_dpi = 100  # number determined by trial and error
    if job_type == "single":  # build and save two charts
        res1 = data.tail(350)  # 350 last trading days, approximately 1.5 years
        mpf.plot(res1, type="line", style="yahoo", title=symbol1 + " Daily Prices last 1.5 years",
                 figsize=(794 / my_plots_dpi, 512 / my_plots_dpi), savefig=filename_1, )
        res1 = data.tail(50)  # 50 last trading days - more days is inconvenient at the chart
        atr_plot = mpf.make_addplot(res1["ATR"], panel=2, ylabel="ATR")
        mpf.plot(res1, type="ohlc", style="yahoo", addplot=atr_plot, \
            title=symbol1 + " Daily Prices last 2.5 months", \
                volume=True, figsize=(794 / my_plots_dpi, 512 / my_plots_dpi), savefig=filename_2, )
    else:  # job_type relative, two symbols, not single, only one chart
        res1 = data.tail(350)  # 350 last trading days, approximately 1.5 years
        mpf.plot(res1, type="line", style="yahoo",
                 title="Relative " + symbol1 + "-" + symbol2 + " Daily Prices last 1.5 years",
                 figsize=(794 / my_plots_dpi, 512 / my_plots_dpi), savefig=filename_1, )
    return filename_1, filename_2


def _add_image_to_msg_root(message_root, image_path, header, subject_text):
    image_add_success_indicator = False
    try:
        fp = open(image_path, "rb")
        msg_image = MIMEImage(fp.read())
        msg_image.add_header("Content-ID", header)
        message_root.attach(msg_image)
        fp.close()
    except Exception as e:
        print(e)
        print("Problem with file", subject_text)
    else:
        image_add_success_indicator = True
    return message_root, image_add_success_indicator


def create_data_for_email(data_store_object, filename_1, filename_2=None):
    msg_root = MIMEMultipart("related")
    msg_root["Subject"] = data_store_object.subject
    msg_root["From"] = data_store_object.config["SMTP_data"]["str_from"]
    msg_root["To"] = data_store_object.config["SMTP_data"]["str_to"]
    msg_root.preamble = "This is a multi-part message in MIME format, with pictures."

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msg_alternative = MIMEMultipart("alternative")
    msg_root.attach(msg_alternative)

    image_1_add_success = False
    image_2_add_success = False
    if filename_2 is not None:
        msg_root, image_2_add_success = _add_image_to_msg_root(
            msg_root, filename_2, "<image2>", data_store_object.subject)
    if filename_1 is not None:
        msg_root, image_1_add_success = _add_image_to_msg_root(
            msg_root, filename_1, "<image1>", data_store_object.subject)

    msg_text = MIMEText('{0}<br>Have a nice day!'.format(data_store_object.note), "html")
    if image_1_add_success and not image_2_add_success:
        msg_text = MIMEText('<img src="cid:image1"><br>{0}<br>Have a nice day!'.format(data_store_object.note), "html")
    if image_1_add_success and image_2_add_success:
        msg_text = MIMEText(
            '<img src="cid:image1"><br><img src="cid:image2"><br>{0}<br>Bye!'.format(data_store_object.note), "html")
    msg_alternative.attach(msg_text)
    send_email_with_data(data_store_object.config, msg_root)
    return msg_root


def send_email_with_data(config_input, msg_data_input):
    smtp = smtplib.SMTP_SSL(config_input["SMTP_data"]["host"], config_input["SMTP_data"]["port"])
    smtp.connect(config_input["SMTP_data"]["host"])
    smtp.login(config_input["SMTP_data"]["login"], config_input["SMTP_data"]["password"])
    smtp.sendmail(config_input["SMTP_data"]["str_from"], config_input["SMTP_data"]["str_to"],
                  msg_data_input.as_string())
    smtp.quit()


def create_portfolio_df_from_worksheets():
    # use credentials to create a client to interact with the Google Drive API
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("./client_secret.json", scope)
    client = gspread.authorize(credentials)
    # Make sure you use the right filename here.
    sheet = client.open("Portfolio")
    sheet_instance1 = sheet.get_worksheet(0)
    all_ideas_rows = pd.DataFrame.from_dict(sheet_instance1.get_all_records())
    assert (not all_ideas_rows.empty), "Now portfolio is empty. Add at least one element. " \
                                       "The worksheet should contain 3 columns: 'Ticker1', 'Ticker2', and 'Note'. " \
                                       "Ticker2 and Note may be empty. Ticker1 - not empty."
    assert ("Ticker1" in all_ideas_rows.columns) & ("Ticker2" in all_ideas_rows.columns) \
           & ("Note" in all_ideas_rows.columns) & ("Type" in all_ideas_rows.columns) \
           & (len(all_ideas_rows.columns) == 4), "Portfolio worksheet should contain 4 columns: " \
                                                 "'Ticker1', 'Ticker2', 'Type', and 'Note'. " \
                                                 "Ticker2 and Note may be empty. Ticker1 ad Type - not empty."
    all_ideas_types = all_ideas_rows['Type'].unique().tolist()
    full_types_list = ['Stocks_ETFs', 'Forex']
    test_condition = all(elem in full_types_list for elem in all_ideas_types)
    assert test_condition, "In portfolio, types allowed are Forex and Stocks_ETFs only"
    all_ideas_rows = all_ideas_rows.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    all_ideas_rows.replace("", np.nan, inplace=True)
    all_ideas_rows_forex = all_ideas_rows[all_ideas_rows['Type'] == 'Forex']
    assert (all_ideas_rows_forex.shape[0] == all_ideas_rows_forex.dropna(subset=['Ticker1', 'Ticker2']).shape[0]), \
        "In Forex rows Ticker1 and Ticker2 must be not empty."
    all_ideas_rows_stocks = all_ideas_rows[all_ideas_rows['Type'] == 'Stocks_ETFs']
    assert (all_ideas_rows_stocks.shape[0] == all_ideas_rows_stocks.dropna(subset=['Ticker1']).shape[0]), \
        "In Stocks_ETFs rows Ticker1 must be not empty."
    return all_ideas_rows


async def _import_forex_row_alpha_vantge(ticker1, ticker2, data_store_object):
    url_backbone = 'https://www.alphavantage.co/query?function=FX_DAILY&outputsize=full&datatype=csv&apikey='
    from_symbol = '&from_symbol='
    from_symbol = from_symbol + ticker1
    to_symbol = '&to_symbol='
    to_symbol = to_symbol + ticker2
    data_url = url_backbone + data_store_object.api_key + from_symbol + to_symbol
    data = await _data_import_and_preprocess(data_url, data_store_object)
    return data


async def _import_stock_ticker(ticker_val, data_store_object, failed_import_tickers, tickers_data_dict):
    print("Importing data", ticker_val, "...")
    try:
        url_backbone = \
            'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&outputsize=full&datatype=csv&apikey='
        symbol_backbone = '&symbol='
        symbol = ticker_val
        data_url = url_backbone + data_store_object.api_key + symbol_backbone + symbol
        data = await _data_import_and_preprocess(data_url, data_store_object)
        data.rename(columns={'volume': 'Volume'}, inplace=True)
    except Exception as e:
        print(e)
        print("Problem in _import_stock_ticker_alpha_vantge -", ticker_val)
        failed_import_tickers.append(ticker_val)
    else:
        tickers_data_dict[ticker_val] = data


async def _data_import_and_preprocess(alpha_vantage_url, data_store_object):
    if data_store_object.last_api_call_time is not None:
        remaining_time = (datetime.datetime.now() - data_store_object.last_api_call_time).total_seconds()
        while remaining_time < 13:
            await asyncio.sleep(remaining_time)
            remaining_time = (datetime.datetime.now() - data_store_object.last_api_call_time).total_seconds()
    data_store_object.last_api_call_time = datetime.datetime.now()
    print('Now call API - ', data_store_object.last_api_call_time)
    data = pd.read_csv(alpha_vantage_url, index_col='timestamp', parse_dates=True)
    data.sort_values(by=['timestamp'], inplace=True, ascending=True)
    data = data.loc[data_store_object.start_date:]
    data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'}, inplace=True)
    data = data.drop(['dividend_amount', 'split_coefficient'], axis=1, errors='ignore')
    data["ATR"] = atr(data, 14)
    print()
    return data


async def _import_tickers_in_row(row, data_store_object):
    if (row['Ticker1'] in data_store_object.all_tickers_data) \
            and ((row['Ticker2'] in data_store_object.all_tickers_data) or pd.isna(row['Ticker2'])):
        return
    if (row['Ticker1'] in data_store_object.tickers_failed_import) \
            or (row['Ticker2'] in data_store_object.tickers_failed_import):
        return
    if row['Type'] == 'Forex':
        combined_ticker_fx = row['Ticker1'] + '-' + row['Ticker2']
        if combined_ticker_fx in data_store_object.all_tickers_data:
            return
        print("Importing data", combined_ticker_fx, "...")
        try:
            imported = await _import_forex_row_alpha_vantge(
                row['Ticker1'], row['Ticker2'], data_store_object)
        except Exception as e:
            print(e)
            data_store_object.tickers_failed_import.append(combined_ticker_fx)
        else:
            imported['Volume'] = 0.0
            data_store_object.all_tickers_data[combined_ticker_fx] = imported
            return
    # stocks_ETFs, not Forex
    if row['Ticker1'] not in data_store_object.all_tickers_data:
        await _import_stock_ticker(row['Ticker1'], data_store_object, data_store_object.tickers_failed_import,
                                   data_store_object.all_tickers_data)
    if row['Ticker2'] not in data_store_object.all_tickers_data and not pd.isna(row['Ticker2']):
        await _import_stock_ticker(row['Ticker2'], data_store_object, data_store_object.tickers_failed_import,
                                   data_store_object.all_tickers_data)
    return


def _add_imaged_and_send_email(data_store_object, ticker_1_val, ticker_2_val, filenames_list):
    data_store_object.subject = create_email_subject(ticker_1_val, ticker_2_val)
    _ = create_data_for_email(data_store_object, filenames_list[0], filenames_list[1])
    # os.remove(filenames_list[0])
    # if filenames_list[1] is not None:
    #     os.remove(filenames_list[1])


async def _process_single_ticker(current_row, data_store_object):
    if current_row['Type'] == 'Forex':
        ticker_1_val = current_row['Ticker1'] + '-' + current_row['Ticker2']
    else:
        ticker_1_val = current_row['Ticker1']
    ticker_2_val = None
    data_store_object.note = current_row['Note']
    print("Processing single ticker", ticker_1_val)
    filename_1, filename_2 = create_charts(data_store_object.all_tickers_data, ticker_1_val, None)
    current_dir = os.getcwd()
    filename_1_path = os.path.join(current_dir, filename_1)
    filename_2_path = os.path.join(current_dir, filename_2)
    if (not os.path.exists(filename_1_path)) or (not os.path.exists(filename_2_path)):
        data_store_object.tickers_failed_processing.append(ticker_1_val)
    else:
        filenames = [filename_1_path, filename_2_path]
        _add_imaged_and_send_email(data_store_object, ticker_1_val, ticker_2_val, filenames)


async def _process_relative_two_tickers(current_row, data_store_object):
    ticker_1_val = current_row['Ticker1']
    ticker_2_val = current_row['Ticker2']
    data_store_object.note = current_row['Note']
    print("Processing Relative two tickers", ticker_1_val, ticker_2_val)
    filename_1, _ = create_charts(data_store_object.all_tickers_data, ticker_1_val, ticker_2_val)
    current_dir = os.getcwd()
    filename_1_path = os.path.join(current_dir, filename_1)
    filename_2_path = None
    if not os.path.exists(filename_1_path):
        data_store_object.tickers_failed_processing.append(ticker_1_val)
        data_store_object.tickers_failed_processing.append(ticker_2_val)
    else:
        filenames = [filename_1_path, filename_2_path]
        _add_imaged_and_send_email(data_store_object, ticker_1_val, ticker_2_val, filenames)


async def process_row(row, data_store_object):
    await _import_tickers_in_row(row, data_store_object)
    if (row['Ticker1'] in data_store_object.tickers_failed_import) \
            or (row['Ticker2'] in data_store_object.tickers_failed_import):
        return
    if row['Type'] == 'Forex':
        combined_ticker_fx = row['Ticker1'] + '-' + row['Ticker2']
        if combined_ticker_fx in data_store_object.tickers_failed_import:
            return
        await _process_single_ticker(row, data_store_object)
        return
    # stocks_ETFs, not Forex
    if row['Ticker1'] in data_store_object.tickers_failed_import:
        return
    if pd.isna(row['Ticker2']) or (row['Ticker2'] in data_store_object.tickers_failed_import):
        await _process_single_ticker(row, data_store_object)
        return
    if not row['Ticker2'] in data_store_object.tickers_failed_import:
        await _process_relative_two_tickers(row, data_store_object)


def process_full():
    config = configparser.ConfigParser()
    config.read("config.ini")
    data_store = DataStore(config)
    png_files = [file for file in glob.glob("static/*.png")]
    for png_file in png_files:
        os.remove(png_file)
    if not os.path.exists('images'):
        os.makedirs('images')
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(*[process_row(row_values, data_store) for _, row_values in data_store.all_ideas.iterrows()])
    loop.run_until_complete(tasks)
    loop.close()

    if (len(data_store.tickers_failed_import) > 0) or (len(data_store.tickers_failed_processing) > 0):
        full_list = data_store.tickers_failed_import + data_store.tickers_failed_processing
        data_store.subject = "PortfolioReport Notification: Wrong tickers in your portfolio"
        data_store.note = "List of problematic tickers: " + str(full_list) + ". Please correct them."
        _ = create_data_for_email(data_store, filename_1=None, filename_2=None)
        print("Sending PortfolioReport Notification: Wrong tickers")
    print("Daily reporting complete!")
    return data_store


if __name__ == "__main__":
    res = process_full()
    print()
    print(res.all_ideas)
    print(res.tickers_failed_processing)
    print(res.tickers_failed_import)

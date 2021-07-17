from unittest import mock
from unittest.mock import MagicMock
import pandas as pd
from django.test import TestCase
from django.conf import settings
import portfoliopositionsreport.portfolio_report_images_not_delete as portfolio_report

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

class PortfolioReportModuleTests(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(PortfolioReportModuleTests, cls).setUpClass()
        cls.portfolio_df = portfolio_report.create_portfolio_df_from_worksheets()
        cls.data_store = portfolio_report.DataStore()

    def test_create_email_subject_single_ticker(self):
        res = portfolio_report.create_email_subject("XBI")
        self.assertEqual(res, "Idea: XBI")

    def test_create_email_subject_two_tickers(self):
        res = portfolio_report.create_email_subject("XBI", "SPY")
        self.assertEqual(res, "Relative XBI SPY")
        
    def test_portfolio_df_is_pandas_dataframe(self):
        assert isinstance(self.portfolio_df, pd.core.frame.DataFrame)
        
    def test_portfolio_df_columns(self):
        self.assertIn("Ticker1", self.portfolio_df.columns)
        self.assertIn( "Ticker2", self.portfolio_df.columns)
        self.assertIn( "Note", self.portfolio_df.columns)
        self.assertIn("Type", self.portfolio_df.columns)
        self.assertEqual(len(self.portfolio_df.columns), 4)        
        
    def test_spy_in_portfolio_df(self):
        spy_search_result = self.portfolio_df[self.portfolio_df.apply(
            lambda row: row.astype(str).str.contains("SPY").any(), axis=1)]
        assert not spy_search_result.empty
        
    def test_create_data_for_email_calls_send_email_with_data(self):
        function_mock = mock.Mock()
        with mock.patch("portfoliopositionsreport.portfolio_report_images_not_delete.send_email_with_data", function_mock):
            res = portfolio_report.create_data_for_email(self.data_store, None, None)
        function_mock.assert_called_once()
        function_mock.assert_called_with(res)
        
    def test_create_data_for_email_result(self):
        function_mock = mock.Mock()
        with mock.patch("portfoliopositionsreport.portfolio_report_images_not_delete.send_email_with_data", function_mock):
            res = portfolio_report.create_data_for_email(self.data_store, None, None)
        self.assertEqual (res["Subject"], self.data_store.subject)
        self.assertEqual (res["From"], settings.SMTP_STR_FROM)
        self.assertEqual (res["To"], settings.SMTP_STR_TO)
        self.assertIn ("This is a multi-part message in MIME format, with pictures", res.as_string())
        self.assertIn ("<br>Have a nice day!", res.as_string())
        
    def test_send_email_with_data(self):
        mock_1 = mock.Mock()
        mock_2 = mock.Mock()
        with mock.patch("portfoliopositionsreport.portfolio_report_images_not_delete.send_email_with_data", mock_1):
            res = portfolio_report.create_data_for_email(self.data_store, None, None)
        with mock.patch("smtplib.SMTP_SSL", mock_2):
            fake_smtp = mock_2(settings.SMTP_HOST, settings.SMTP_PORT)
            portfolio_report.send_email_with_data(res)
            assert mock_2.call_count == 2
            fake_smtp.connect.assert_called_once_with(settings.SMTP_HOST)
            fake_smtp.login.assert_called_once_with(settings.SMTP_LOGIN, settings.SMTP_PASSWORD)
            fake_smtp.sendmail.assert_called_once_with(settings.SMTP_STR_FROM, settings.SMTP_STR_TO, res.as_string())
            fake_smtp.quit.assert_called_once()
    
    def test_portfolio_report_singles_and_doble_tickers_separation(self):
        import_tickers_in_row_mock = AsyncMock()
        process_single_ticker_mock = AsyncMock()
        process_relative_two_tickers_mock = AsyncMock()
        os_remove_mock = mock.Mock()
        with mock.patch("portfoliopositionsreport.portfolio_report_images_not_delete._import_tickers_in_row", import_tickers_in_row_mock):
            with mock.patch("portfoliopositionsreport.portfolio_report_images_not_delete._process_single_ticker", process_single_ticker_mock):
                with mock.patch("portfoliopositionsreport.portfolio_report_images_not_delete._process_relative_two_tickers", process_relative_two_tickers_mock):
                    with mock.patch("os.remove", os_remove_mock):
                        res = portfolio_report.process_full()
        ideas = res.all_ideas
        assert isinstance(ideas, pd.core.frame.DataFrame)
        num_rows = ideas.shape[0]
        self.assertEqual (num_rows, import_tickers_in_row_mock.call_count)
        num_singles = ideas[(ideas['Type'] == 'Forex') | pd.isna(ideas['Ticker2'])].shape[0]
        num_relative_two_ticker_cases = num_rows - num_singles
        self.assertEqual (num_singles, process_single_ticker_mock.call_count)
        self.assertEqual (num_relative_two_ticker_cases, process_relative_two_tickers_mock.call_count)
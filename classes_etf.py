import pandas as pd
class IShareETF:
    """
    A helper class to parse iShares ETF Excel files and store 
    both the metadata (e.g., inception date, number of securities) 
    and the holdings in an easy-to-use structure.
    """
    def __init__(self, file_path):
        """
        file_path: Path to the Excel file (e.g. "ACWI_holdings.xlsx").
        """
        self.file_path = file_path
        self.metadata = {}
        self.holdings = pd.DataFrame()
        
        # Parse the file
        self._parse_file()

    def _parse_file(self):
        """
        Private method that reads the raw Excel sheet and populates:
          - self.metadata (dictionary)
          - self.holdings (DataFrame)
        """
        # 1) First, read the entire file to grab those first 5 lines
        raw_df = pd.read_excel(self.file_path, engine="openpyxl")

        self.metadata["fund_name"] = str(raw_df.iloc[0, 0])
        self.metadata["inception_date"] = str(raw_df.iloc[1, 1])
        self.metadata["num_securities"] = raw_df.iloc[3, 1]
        # ... parse more lines / columns as needed

        # 2) We assume real holdings data starts at row 5 (0-based) 
        #    and that row 5 includes column headers for the holdings.
        #    We'll do a separate read with skiprows=.
        self.holdings = pd.read_excel(
            self.file_path,
            skiprows=7,       # skip the top 5 lines
            engine="openpyxl" # or remove if default works
        )

        # Optionally rename columns if you want consistent naming

        self.holdings.columns= ['Ticker', 'Name', 'Sector', 'Asset_Class',
           'Market_Value', 'Weight', 'Notional_Value', 'Quantity',
           'Price', 'Location', 'Exchange', 'Currency']


    def get_country_exposure(self):
        """
        Group holdings by country and sum the weight.
        Returns a DataFrame with columns: [Location, Weight].
        """
        if "Location" not in self.holdings.columns or "Weight" not in self.holdings.columns:
            return pd.DataFrame()

        exposure = self.holdings.groupby("Location")["Weight"].sum().reset_index()
        exposure.sort_values(by="Weight", ascending=False, inplace=True)
        return exposure

    def __repr__(self):
        # Simple representation showing what’s in the object.
        return (
            f"IShareETF(\n"
            f"  file_path={self.file_path},\n"
            f"  fund_name={self.metadata.get('fund_name')},\n"
            f"  inception_date={self.metadata.get('inception_date')},\n"
            f"  num_securities={self.metadata.get('num_securities')},\n"
            f"  holdings.shape={self.holdings.shape}\n"
            f")"
        )

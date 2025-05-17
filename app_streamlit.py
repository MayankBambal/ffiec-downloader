"""
Streamlit app for FFIEC Call Reports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from ffiec_call_reports import FFIECClient, get_mapping_dict, apply_mapping

def main():
    st.title("FFIEC Call Reports Downloader")
    
    # Sidebar for credentials
    with st.sidebar:
        st.header("Credentials")
        username = st.text_input("Username:", value="mbambal")
        passphrase = st.text_input("Passphrase:", value="IuwnFdSSpFRzsRTX9dKx", type="password")
    
    # Main interface
    st.header("Input Parameters")
    
    # Input fields
    rssd_ids_input = st.text_input(
        "Enter RSSD IDs (comma-separated):",
        value="1842065",
        help="Enter multiple RSSD IDs separated by commas (e.g., 1842065, 1842066)"
    )
    
    period_end_date = st.date_input(
        "Select Period End Date:",
        value=datetime(2019, 3, 31),
        format="YYYY/MM/DD"
    )
    
    if st.button("Download Call Reports"):
        try:
            # Initialize client
            client = FFIECClient(username, passphrase)
            
            # Process RSSD IDs
            rssd_ids = [id.strip() for id in rssd_ids_input.split(',') if id.strip()]
            
            if not rssd_ids:
                st.error("Please enter at least one RSSD ID")
                return
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Get reports
            reports = []
            for i, rssd_id in enumerate(rssd_ids):
                status_text.text(f"Processing RSSD ID: {rssd_id}")
                
                try:
                    report = client.get_call_report(rssd_id, period_end_date)
                    if report is not None:
                        reports.append(report)
                except Exception as e:
                    st.warning(f"Error processing RSSD ID {rssd_id}: {str(e)}")
                
                progress_bar.progress((i + 1) / len(rssd_ids))
            
            if not reports:
                st.error("No data was retrieved for any RSSD ID.")
                return
            
            # Combine all reports
            all_data = pd.concat([report.to_dataframe() for report in reports], ignore_index=True)
            
            # Display raw data
            st.subheader("Raw Data")
            st.dataframe(all_data)
            
            # Apply mapping
            mapping_dict = get_mapping_dict()
            mapped_data = apply_mapping(all_data, mapping_dict)
            
            # Display mapped data
            st.subheader("Mapped Data")
            st.dataframe(mapped_data)
            
            # Save to CSV button
            csv = mapped_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"call_reports_{period_end_date.strftime('%Y_%m_%d')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 
import os
import json
import pandas as pd
import zipfile
from io import TextIOWrapper
import streamlit as st
import time

st.set_page_config(page_title="GST Data Converter", layout="wide")
st.title("📊 GST Data Converter")
st.markdown("Upload a ZIP file containing GSTR-2B JSONs. Select month(s) to extract and generate an Excel file.")

uploaded_zip = st.file_uploader("📎 Upload ZIP file", type="zip")

if uploaded_zip:
    all_months = set()
    all_entries = []

    def get_month_tag(filename):
        for part in filename.split('_'):
            if part.isdigit() and len(part) == 6:
                return f"{part[:2]}-{part[2:]}"
        return "Unknown"

    with zipfile.ZipFile(uploaded_zip, 'r') as zipf:
        for name in zipf.namelist():
            if ("summary" in name.lower()) or not name.lower().endswith(".json") or name.endswith("/"):
                continue
            try:
                with zipf.open(name) as file:
                    data = json.load(TextIOWrapper(file, 'utf-8'))

                month = get_month_tag(name)
                all_months.add(month)
                docdata = data.get("data", {}).get("docdata", {})

                for category, entries in docdata.items():
                    for record in entries:
                        if not isinstance(record, dict):
                            continue
                        ctin = record.get("ctin", "")
                        trdnm = record.get("trdnm", "")
                        supprd = record.get("supprd", "")
                        supfildt = record.get("supfildt", "")

                        if category in ["cdnr", "cdnra"]:
                            for note in record.get("nt", []):
                                for item in note.get("items", [{}]):
                                    row = {
                                        "Category": category,
                                        "Month": month,
                                        "Trade Name": trdnm,
                                        "CTIN": ctin,
                                        "Supplier Period": supprd,
                                        "Supplier Filing Date": supfildt,
                                        "Invoice Number": note.get("ntnum"),
                                        "Invoice Date": note.get("nt_dt"),
                                        "Original Invoice Number": note.get("oinum"),
                                        "Original Invoice Date": note.get("oidt"),
                                        "Invoice Type": note.get("typ"),
                                        "Reverse Charge": note.get("rev"),
                                        "ITC Available": note.get("itcavl"),
                                        "Reason": note.get("rsn"),
                                        "POS": note.get("pos", record.get("pos", "")),
                                        "Invoice Value": note.get("val", ""),
                                        "Taxable Value": item.get("txval", ""),
                                        "SGST": item.get("sgst", 0),
                                        "CGST": item.get("cgst", 0),
                                        "IGST": item.get("igst", 0),
                                        "CESS": item.get("cess", 0)
                                    }
                                    all_entries.append(row)
                        else:
                            for inv in record.get("inv", []):
                                for item in inv.get("items", [{}]):
                                    row = {
                                        "Category": category,
                                        "Month": month,
                                        "Trade Name": trdnm,
                                        "CTIN": ctin,
                                        "Supplier Period": supprd,
                                        "Supplier Filing Date": supfildt,
                                        "Invoice Number": inv.get("inum"),
                                        "Invoice Date": inv.get("dt"),
                                        "Invoice Type": inv.get("typ"),
                                        "Reverse Charge": inv.get("rev"),
                                        "ITC Available": inv.get("itcavl"),
                                        "Reason": inv.get("rsn"),
                                        "POS": inv.get("pos"),
                                        "Source Type": inv.get("srctyp", ""),
                                        "IRN": inv.get("irn", ""),
                                        "IRN Generation Date": inv.get("irngendate", ""),
                                        "Invoice Value": inv.get("val"),
                                        "Taxable Value": item.get("txval", inv.get("txval")),
                                        "SGST": item.get("sgst", inv.get("sgst", 0)),
                                        "CGST": item.get("cgst", inv.get("cgst", 0)),
                                        "IGST": item.get("igst", inv.get("igst", 0)),
                                        "CESS": item.get("cess", inv.get("cess", 0))
                                    }
                                    all_entries.append(row)
            except Exception as e:
                st.error(f"Error processing {name}: {e}")

    if all_entries:
        select_all = st.checkbox("Select All Months")
        selected_months = st.multiselect("Select Month(s) to include in Excel:", sorted(all_months), default=sorted(all_months) if select_all else [])
        output_name = st.text_input("Enter output Excel filename (without .xlsx):", value="GST_Data_Report")

        run_conversion = st.button("🚀 Convert to Excel")

        if run_conversion:
            if selected_months:
                start_time = time.time()

                df_all = pd.DataFrame(all_entries)
                df_filtered = df_all[df_all['Month'].isin(selected_months)]

                output_excel = f"{output_name}.xlsx"
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    for cat in df_filtered['Category'].unique():
                        df_cat = df_filtered[df_filtered['Category'] == cat].drop(columns=['Category'])
                        if not df_cat.empty:
                            df_cat.to_excel(writer, sheet_name=cat[:31], index=False)

                total_time = time.time() - start_time
                st.success(f"✅ Excel generated in {total_time:.2f} seconds.")

                with open(output_excel, 'rb') as f:
                    st.download_button("📥 Download Excel", f, file_name=output_excel, disabled=False)
            else:
                st.warning("Please select at least one month before converting.")
    else:
        st.warning("No valid data found in uploaded ZIP.")
